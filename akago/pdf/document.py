from functools import lru_cache
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from akago.config import STATIC_DIR
from akago.models.request import AugmentationRequest, Gender


def init_pdf_creator() -> None:
    font = TTFont("DejaVu", STATIC_DIR / "DejaVuSans.ttf")

    # Register a font that supports Polish characters.
    pdfmetrics.registerFont(font)


def create_document(request: AugmentationRequest) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    elements = []

    def create_section(title: str, element, *, spacer: bool = True) -> None:
        elements.append(Paragraph(title, bold_style))
        elements.append(element)

        if spacer:
            elements.append(Spacer(1, 0.3 * inch))

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=16,
        leading=20,
        alignment=1,
        fontName="DejaVu",
        spaceAfter=20,
    )
    bold_style = ParagraphStyle(
        name="BoldStyle", fontSize=12, fontName="DejaVu", leading=14, spaceAfter=6
    )
    table_style = TableStyle(
        [
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )

    elements.append(_get_logo())
    elements.append(Spacer(1, 0.2 * inch))

    # Title
    elements.append(
        Paragraph("Wniosek o Personalizowaną Augmentację Cybernetyczną", title_style)
    )

    # Section: Personal Information
    personal_info = [
        ["Imię i nazwisko:", request.fullname],
        ["Adres zamieszkania:", request.address],
        ["Adres e-mail:", request.email],
        ["Numer telefonu:", request.phoneNumber],
        ["Data urodzenia:", request.birthDate.strftime("%d.%m.%Y")],
        ["Płeć:", _gender_to_str(request.sex)],
        ["Numer identyfikacyjny:", request.idNumber],
    ]
    personal_table = Table(
        personal_info, colWidths=[2.5 * inch, 3.5 * inch], style=table_style
    )
    create_section("Dane personalne", personal_table)

    # Section: Augmentation Details
    augmentation_info = [
        ["Rodzaj augmentacji:", request.implantType],
        ["Cel augmentacji:", request.implantPurpose],
        ["Osobiste preferencje estetyczne:", request.estheticPreferences],
        [
            "Dodatkowe opcje:",
            ", ".join(
                filter(
                    lambda s: len(s) > 0,
                    map(lambda f: f.feature, request.additonalFeatures),
                )
            )
            or "brak",
        ],
        ["Termin instalacji:", request.installationDate],
        ["Preferowana placówka:", request.preferredFacility],
        [
            "Dodatkowe wymagania:",
            ", ".join(
                filter(
                    lambda s: len(s) > 0,
                    map(lambda r: r.requirement, request.additionalRequirements),
                )
            )
            or "brak",
        ],
    ]
    augmentation_table = Table(
        augmentation_info, colWidths=[2.5 * inch, 3.5 * inch], style=table_style
    )
    create_section("Dane dotyczące augmentacji", augmentation_table)

    # Section: Medical Information
    medical_info = [
        ["Grupa krwi:", request.bloodGroup],
    ]
    medical_table = Table(
        medical_info, colWidths=[2.5 * inch, 3.5 * inch], style=table_style
    )
    create_section("Informacje medyczne", medical_table)

    # Section: Medical History
    medical_entries = list(filter(lambda m: not m.is_empty(), request.medicalHistory))
    medical_history_info = []

    if len(medical_entries) == 0:
        medical_history_info.append(["Brak", "", "", ""])
    else:
        medical_history_info.append(
            ["Choroba", "Data rozpoznania", "Leczenie", "Aktualny status"]
        )

        for entry in medical_entries:
            medical_history_info.append(
                [
                    entry.disease,
                    entry.diagnosisDate,
                    entry.treatment,
                    entry.currentStatus,
                ]
            )

    medical_history_table = Table(
        medical_history_info, colWidths=[1.5 * inch] * 4, style=table_style
    )
    create_section("Historia chorób", medical_history_table)

    # Section: Augmentation History
    augmentations = list(filter(lambda a: not a.is_empty(), request.implantHistory))
    augmentation_history_info = []

    if len(augmentations) == 0:
        augmentation_history_info.append(["Brak", "", "", ""])
    else:
        augmentation_history_info.append(
            ["Rodzaj augmentacji", "Producent", "Data instalacji", "Numer seryjny"]
        )

        for entry in augmentations:
            augmentation_history_info.append(
                [
                    entry.type,
                    entry.producer,
                    entry.installationDate,
                    entry.serialNumber,
                ]
            )

    augmentation_history_table = Table(
        augmentation_history_info, colWidths=[1.5 * inch] * 4, style=table_style
    )
    create_section("Historia augmentacji", augmentation_history_table)

    # Section: Medication History
    medications = list(filter(lambda m: not m.is_empty(), request.medications))
    medication_info = []

    if len(medications) == 0:
        medication_info.append(["Brak", "", "", ""])
    else:
        medication_info.append(["Nazwa leku", "Dawka", "Częstotliwość", "Uwagi"])

        for medication in medications:
            medication_info.append(
                [
                    medication.name,
                    medication.dose,
                    medication.frequency,
                    medication.comment,
                ]
            )

    medication_table = Table(
        medication_info, colWidths=[1.5 * inch] * 4, style=table_style
    )
    print([1.5 * inch] * 4)
    create_section("Lista aktualnie przyjmowanych leków", medication_table)

    # Section: Consents
    elements.append(Paragraph("Zgody i oświadczenia", bold_style))
    consents = [
        [
            "Zgoda na przetwarzanie danych osobowych:",
            "Tak" if request.personalDataConsent else "Nie",
        ],
        [
            "Zgoda na przeprowadzenie instalacji wszczepu:",
            "Tak" if request.intallationConsent else "Nie",
        ],
    ]

    consent_table = Table(
        consents, colWidths=[3.5 * inch, 1.5 * inch], style=table_style
    )
    elements.append(consent_table)

    doc.build(elements)

    return buf.getvalue()


def _gender_to_str(gender: Gender) -> str:
    match gender:
        case Gender.MALE:
            return "mężczyzna"
        case Gender.FEMALE:
            return "kobieta"
        case Gender.OTHER:
            return "inna"


@lru_cache
def _get_logo() -> Image:
    return Image(STATIC_DIR / "logo.png", width=1.2 * inch, height=1.2 * inch)
