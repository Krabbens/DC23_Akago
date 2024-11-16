from typing import Optional

from pydantic import BaseModel


class AugmentationFeature(BaseModel):
    feature: str


class AugmentationRequirement(BaseModel):
    requirement: str


class MedicalHistoryEntry(BaseModel):
    disease: str
    diagnosisDate: str
    treatment: str
    currentStatus: str


class ImplantHistoryEntry(BaseModel):
    type: str
    producer: str
    installationDate: str
    serialNumber: str


class Medication(BaseModel):
    name: str
    dose: str
    frequency: str
    comment: str


# TODO: This needs to be changed to correct types (such as date) and optionality of some properties
# needs to be changed.
class AugmentationRequest(BaseModel):
    fullname: str
    address: str
    phoneNumber: str
    email: str
    birthDate: str
    sex: Optional[str] = None
    idNumber: str
    implantType: str
    implantPurpose: str
    estheticPreferences: str
    additonalFeatures: list[AugmentationFeature]
    installationDate: str
    preferredFacility: str
    additionalRequirements: list[AugmentationRequirement]
    bloodGroup: str
    medicalHistory: list[MedicalHistoryEntry]
    implantHistory: list[ImplantHistoryEntry]
    medications: list[Medication]
    personalDataConsent: Optional[str] = None
    intallationConsent: Optional[str] = None
