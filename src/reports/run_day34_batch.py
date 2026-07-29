from pathlib import Path
import pandas as pd

from tearsheet import build_pdf, companies

BASE_DIR = Path(__file__).resolve().parents[2]

REPORT_DIR = BASE_DIR / "reports" / "tearsheets"
OUTPUT = BASE_DIR / "output"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

skipped = []

generated = 0

print("=" * 50)
print("Generating Company Tearsheets")
print("=" * 50)

for company in companies:

    try:

        build_pdf(company)

        generated += 1

    except Exception as e:

        skipped.append(
            {
                "company_id": company,
                "reason": str(e)
            }
        )

        print(f"Skipped {company}")

print("\nGeneration Completed")

print("Generated :", generated)

print("Skipped :", len(skipped))

if skipped:

    skipped_df = pd.DataFrame(skipped)

else:

    skipped_df = pd.DataFrame(
        columns=[
            "company_id",
            "reason"
        ]
    )

skipped_df.to_csv(

    OUTPUT / "skipped_tearsheets.csv",

    index=False

)

print("\nSkipped file saved.")

pdfs = list(REPORT_DIR.glob("*_tearsheet.pdf"))

print("\nVerification")

print("-------------------------")

print("PDF Files :", len(pdfs))

print("-------------------------")

for pdf in pdfs[:10]:

    print(pdf.name)

print("\nDay 34 Batch Generation Completed Successfully")