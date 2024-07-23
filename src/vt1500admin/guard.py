#!/usr/bin/env python

from typing import Callable, Dict, List, Union
from os import path, remove
import os, pathlib

from shutil import rmtree, make_archive
from random import randint
from dataclasses import asdict

from unittest import TestCase

from electionguard.type import BallotId
from electionguard.utils import get_optional

# Step 0 - Configure Election
from electionguard.constants import ElectionConstants, get_constants
from electionguard.election import CiphertextElectionContext
from electionguard.manifest import Manifest, InternalManifest

# Step 1 - Key Ceremony
from electionguard.guardian import Guardian, GuardianRecord, PrivateGuardianRecord
from electionguard.key_ceremony_mediator import KeyCeremonyMediator

# Step 2 - Encrypt Votes
from electionguard.ballot import (
    BallotBoxState,
    CiphertextBallot,
    PlaintextBallot,
    SubmittedBallot,
)
from electionguard.encrypt import EncryptionDevice
from electionguard.encrypt import EncryptionMediator

# Step 3 - Cast and Spoil
from electionguard.data_store import DataStore
from electionguard.ballot_box import BallotBox, get_ballots

# Step 4 - Decrypt Tally
from electionguard.tally import (
    PublishedCiphertextTally,
    tally_ballots,
    CiphertextTally,
    PlaintextTally,
)
from electionguard.decryption_mediator import DecryptionMediator
from electionguard.election_polynomial import LagrangeCoefficientsRecord

# Step 5 - Publish and Verify
from electionguard.serialize import from_file, construct_path, to_file
from electionguard_tools.helpers.export import (
    COEFFICIENTS_FILE_NAME,
    DEVICES_DIR,
    GUARDIANS_DIR,
    PRIVATE_DATA_DIR,
    SPOILED_BALLOTS_DIR,
    SUBMITTED_BALLOTS_DIR,
    ELECTION_RECORD_DIR,
    SUBMITTED_BALLOT_PREFIX,
    SPOILED_BALLOT_PREFIX,
    CONSTANTS_FILE_NAME,
    CONTEXT_FILE_NAME,
    DEVICE_PREFIX,
    ENCRYPTED_TALLY_FILE_NAME,
    GUARDIAN_PREFIX,
    MANIFEST_FILE_NAME,
    TALLY_FILE_NAME,
    export_private_data,
    export_record,
)

from electionguard_tools.factories.ballot_factory import BallotFactory
from electionguard_tools.factories.election_factory import (
    ElectionFactory,
    NUMBER_OF_GUARDIANS,
)
from electionguard_tools.helpers.election_builder import ElectionBuilder

from .models import Election, Voter
from .forms import BallotForm


devices_directory = path.join(ELECTION_RECORD_DIR, DEVICES_DIR)
guardians_directory = path.join(ELECTION_RECORD_DIR, GUARDIANS_DIR)
submitted_ballots_directory = path.join(ELECTION_RECORD_DIR, SUBMITTED_BALLOTS_DIR)
spoiled_ballots_directory = path.join(ELECTION_RECORD_DIR, SPOILED_BALLOTS_DIR)
NUMBER_OF_GUARDIANS = 1
QUORUM = 1


REMOVE_RAW_OUTPUT = True
REMOVE_ZIP_OUTPUT = True

class ElectionRuntime():

    guardian_records: List[GuardianRecord] = []
    private_guardian_records: List[PrivateGuardianRecord] = []
    manifest: Manifest
    election_builder: ElectionBuilder
    internal_manifest: InternalManifest
    context: CiphertextElectionContext
    constants: ElectionConstants

    # Step 1 - Key Ceremony
    mediator: KeyCeremonyMediator
    guardians: List[Guardian] = []

    # Step 2 - Encrypt Votes
    device: EncryptionDevice
    encrypter: EncryptionMediator
    plaintext_ballots: List[PlaintextBallot]
    ciphertext_ballots: List[CiphertextBallot] = []

    # Step 3 - Cast and Spoil
    ballot_box: BallotBox
    submitted_ballots: Dict[BallotId, SubmittedBallot]
    ballot_store: DataStore[BallotId, SubmittedBallot]


    # Step 4 - Decrypt Tally
    ciphertext_tally: CiphertextTally
    plaintext_tally: PlaintextTally
    plaintext_spoiled_ballots: Dict[str, PlaintextTally]
    decryption_mediator: DecryptionMediator
    lagrange_coefficients: LagrangeCoefficientsRecord

    def setup_election(self, election: Election, voters: List[Voter]) -> None:
        """
        To conduct an election, load an `Manifest` file.
        """

        # Step 0 - Configure Election

        root_path = str(pathlib.Path(__file__).parent.parent.parent.resolve())
        self.manifest = ElectionFactory().get_manifest_from_filename(os.path.join(root_path, "data", "minimal_manifest.json"))
        
        print(
            f"""
            {'-'*40}\n
            # Election Summary:
            # Scope: {self.manifest.election_scope_id}
            # Geopolitical Units: {len(self.manifest.geopolitical_units)}
            # Parties: {len(self.manifest.parties)}
            # Candidates: {len(self.manifest.candidates)}
            # Contests: {len(self.manifest.contests)}
            # Ballot Styles: {len(self.manifest.ballot_styles)}\n
            {'-'*40}\n
            """
        )

        # Create an Election Builder
        self.election_builder = ElectionBuilder(
            NUMBER_OF_GUARDIANS, QUORUM, self.manifest
        )


        # Setup Guardians
        for i in range(NUMBER_OF_GUARDIANS):
            self.guardians.append(
                Guardian.from_nonce(
                    str(i + 1),
                    i + 1,
                    NUMBER_OF_GUARDIANS,
                    QUORUM,
                )
            )

        # Setup Mediator
        self.mediator = KeyCeremonyMediator(
            "mediator_1", self.guardians[0].ceremony_details
        )

        # ROUND 1: Public Key Sharing
        # Announce
        for guardian in self.guardians:
            self.mediator.announce(guardian.share_key())

        # Share Keys
        for guardian in self.guardians:
            announced_keys = get_optional(self.mediator.share_announced())
            for key in announced_keys:
                if guardian.id is not key.owner_id:
                    guardian.save_guardian_key(key)


        # FINAL: Publish Joint Key
        joint_key = self.mediator.publish_joint_key()


        # Build the Election
        self.election_builder.set_public_key(get_optional(joint_key).joint_public_key)
        self.election_builder.set_commitment_hash(
            get_optional(joint_key).commitment_hash
        )
        self.internal_manifest, self.context = get_optional(
            self.election_builder.build()
        )
        self.constants = get_constants()

        # Configure the Ballot Box
        self.ballot_store = DataStore()
        self.ballot_box = BallotBox(
            self.internal_manifest, self.context, self.ballot_store
        )

        # # Saving election data to file
        # election_path = os.path.join(root_path, "data", "election")

        # to_file(manifest, "manifest", election_path)
        # to_file(constants, "constants", election_path)
        # to_file(ballot_box, "ballot_box", election_path)

        # # guardian_records = [guardian.publish() for guardian in self.guardians]
        # guardian_record = self.guardians[0].publish()
        # private_guardian_record = self.guardians[0].export_private_data()

        # # export_private_data(private_guardian_records)
        # # to_file(mediator, "mediator", election_path)
        # to_file(guardian_record, "guardian", election_path)
        # to_file(private_guardian_record, "guardian_private", election_path)

    def cast_vote(self, vote: bool) -> None:
        """
        Using the `CiphertextElectionContext` encrypt ballots for the election.
        """



        # Configure the Encryption Device
        self.device = ElectionFactory.get_encryption_device()
        self.encrypter = EncryptionMediator(
            self.internal_manifest, self.context, self.device
        )

        # Load some Ballots

        if vote:
            plaintext_ballot = BallotFactory()._get_ballot_from_file(os.path.join(ballot_path, "for_ballot.json"))
        else:
            plaintext_ballot = BallotFactory()._get_ballot_from_file(os.path.join(ballot_path, "against_ballot.json"))

        # Encrypt the Ballot
        encrypted_ballot = self.encrypter.encrypt(plaintext_ballot)
        ciphertext_ballot = get_optional(encrypted_ballot)

        # Next, we cast or spoil the ballots


        # cast the ballots
        # for ballot in ciphertext_ballots:

        submitted_ballot = self.ballot_box.cast(ciphertext_ballot)


    def decrypt_tally(self) -> None:
        """
        Homomorphically combine the selections made on all of the cast ballots
        and use the Available Guardians to decrypt the combined tally.
        In this way, no individual voter's cast ballot is ever decrypted drectly.
        """

        
        # Generate a Homomorphically Accumulated Tally of the ballots
        ciphertext_tally = get_optional(
            tally_ballots(self.ballot_store, self.internal_manifest, self.context)
        )
        self.submitted_ballots = get_ballots(self.ballot_store, BallotBoxState.SPOILED)

        # Configure the Decryption
        submitted_ballots_list = list(self.submitted_ballots.values())
        self.decryption_mediator = DecryptionMediator(
            "decryption-mediator",
            self.context,
        )

        # Announce each guardian as present
        count = 0
        for guardian in self.guardians:
            guardian_key = guardian.share_key()
            tally_share = guardian.compute_tally_share(
                self.ciphertext_tally, self.context
            )
            ballot_shares = guardian.compute_ballot_shares(
                submitted_ballots_list, self.context
            )
            self.decryption_mediator.announce(
                guardian_key, get_optional(tally_share), ballot_shares
            )
            count += 1

        self.lagrange_coefficients = LagrangeCoefficientsRecord(
            self.decryption_mediator.get_lagrange_coefficients()
        )

        # Get the plaintext Tally
        self.plaintext_tally = get_optional(
            self.decryption_mediator.get_plaintext_tally(
                self.ciphertext_tally, self.manifest
            )
        )


        # Get the plaintext Spoiled Ballots
        self.plaintext_spoiled_ballots = get_optional(
            self.decryption_mediator.get_plaintext_ballots(
                submitted_ballots_list, self.manifest
            )
        )


    def publish_results(self) -> None:
        """Publish results/artifacts of the election."""

        self.guardian_records = [guardian.publish() for guardian in self.guardians]
        self.private_guardian_records = [
            guardian.export_private_data() for guardian in self.guardians
        ]

        export_record(
            self.manifest,
            self.context,
            self.constants,
            [self.device],
            self.ballot_store.all(),
            self.plaintext_spoiled_ballots.values(),
            self.ciphertext_tally.publish(),
            self.plaintext_tally,
            self.guardian_records,
            self.lagrange_coefficients,
        )

        export_private_data(
            self.plaintext_ballots,
            self.ciphertext_ballots,
            self.private_guardian_records,
        )

        ZIP_SUFFIX = "zip"
        make_archive(ELECTION_RECORD_DIR, ZIP_SUFFIX, ELECTION_RECORD_DIR)
        make_archive(PRIVATE_DATA_DIR, ZIP_SUFFIX, PRIVATE_DATA_DIR)

        self.deserialize_data()

        if self.REMOVE_RAW_OUTPUT:
            rmtree(ELECTION_RECORD_DIR)
            rmtree(PRIVATE_DATA_DIR)

        if self.REMOVE_ZIP_OUTPUT:
            remove(f"{ELECTION_RECORD_DIR}.{ZIP_SUFFIX}")
            remove(f"{PRIVATE_DATA_DIR}.{ZIP_SUFFIX}")



ELECTION_RUNTIME = ElectionRuntime()
