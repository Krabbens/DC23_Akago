from datetime import date
from enum import Enum

from beanie import Document
from pydantic import BaseModel, EmailStr


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AugmentationFeature(BaseModel):
    feature: str


class AugmentationRequirement(BaseModel):
    requirement: str


class MedicalHistoryEntry(BaseModel):
    disease: str
    diagnosisDate: str
    treatment: str
    currentStatus: str

    def is_empty(self) -> bool:
        return (
            self.disease == ""
            and self.diagnosisDate == ""
            and self.treatment == ""
            and self.currentStatus == ""
        )


class ImplantHistoryEntry(BaseModel):
    type: str
    producer: str
    installationDate: str
    serialNumber: str

    def is_empty(self) -> bool:
        return (
            self.type == ""
            and self.producer == ""
            and self.installationDate == ""
            and self.serialNumber == ""
        )


class Medication(BaseModel):
    name: str
    dose: str
    frequency: str
    comment: str

    def is_empty(self) -> bool:
        return (
            self.name == ""
            and self.dose == ""
            and self.frequency == ""
            and self.comment == ""
        )


# TODO: This needs to be changed to correct types (such as date) and optionality of some properties
# needs to be changed.
class AugmentationRequest(BaseModel):
    fullname: str
    address: str
    phoneNumber: str
    email: EmailStr
    birthDate: date
    sex: Gender
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
    personalDataConsent: str | None = None
    intallationConsent: str | None = None


class AugmentationDocument(Document):
    file_id: str
    filename: str
    email: EmailStr
    gender: Gender
