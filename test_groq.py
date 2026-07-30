from llm.groq_service import analyze_report

sample_report = """
Patient Name: John

Age: 45

Hemoglobin: 11.2 g/dL

WBC: 9000 /µL

Platelets: 220000 /µL
"""

response = analyze_report(sample_report)

print(response)