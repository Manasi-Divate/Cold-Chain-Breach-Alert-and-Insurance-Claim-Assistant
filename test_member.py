from utils.report_generator import generate_fda_report
from utils.insurance_generator import generate_insurance_claim
from utils.docx_generator import save_docx


sample_excursion = {

    "bag_id": "BAG_001",

    "start_time":
    "2026-05-30 10:00:00",

    "end_time":
    "2026-05-30 12:00:00",

    "duration_minutes":
    120,

    "max_temperature":
    9.5,

    "severity":
    "Medium"
}


fda_report = generate_fda_report(
    sample_excursion
)

insurance_report = generate_insurance_claim(
    sample_excursion
)

print("\n========== FDA REPORT ==========\n")
print(fda_report)

print("\n========== INSURANCE REPORT ==========\n")
print(insurance_report)

save_docx(
    fda_report,
    "FDA_Report.docx"
)

save_docx(
    insurance_report,
    "Insurance_Claim.docx"
)

print("\nReports Generated Successfully")