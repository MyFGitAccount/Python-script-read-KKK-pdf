import fitz  # PyMuPDF
import re

pdf_path = "MTT_2526S1_V2_20250911.pdf"
output_js = "courses.js"

doc = fitz.open(pdf_path)
courses = []

# Regex patterns
code_re = re.compile(r"[A-Z]{3,4}\d{4}[A-Z0-9]*")   # Course code like CCAH3003
class_re = re.compile(r"^[A-Z]{2}\d+$")             # Class number like CL01, CT02
time_re = re.compile(r"\d{2}:\d{2}")                # Times like 08:30
weekday_re = re.compile(r"\b[1-7]\b")               # Weekday digits 1–7

print(f"Extracting from {doc.page_count} pages...")

current_code = ""
current_class = ""
current_name = ""
pending_name = False

for page_num, page in enumerate(doc, start=1):
    text = page.get_text("text")
    lines = text.splitlines()

    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue

        # Detect course code
        if code_re.fullmatch(line):
            current_code = line
            continue

        # Detect class number
        if class_re.fullmatch(line) and current_code:
            current_class = line
            pending_name = True
            continue

        # Capture course name (line after class number, without times)
        if pending_name and not time_re.search(line):
            current_name = line.strip()
            pending_name = False
            continue

        # Detect course detail lines (must contain times)
        times = time_re.findall(line)
        if current_code and current_class and len(times) >= 2:
            try:
                start_time, end_time = times[0], times[1]

                # Try to extract weekday
                weekday_match = weekday_re.search(line)
                weekday = int(weekday_match.group()) if weekday_match else None

                # Room is usually last token
                parts = line.split()
                room = parts[-1]

                courses.append({
                    "code": current_code,
                    "classNo": current_class,
                    "name": current_name,
                    "weekday": weekday,
                    "startTime": start_time,
                    "endTime": end_time,
                    "room": room
                })
            except Exception as e:
                print(f"[Page {page_num}] Parse error: {e} | Line: {line}")
                continue

# Sort results
courses.sort(key=lambda x: (x["code"], x["classNo"]))

# Write JS file
with open(output_js, "w", encoding="utf-8") as f:
    f.write("const courses = [\n")
    for c in courses:
        f.write(
            f'  {{ code: "{c["code"]}", classNo: "{c["classNo"]}", name: "{c["name"]}", '
            f'weekday: {c["weekday"]}, startTime: "{c["startTime"]}", endTime: "{c["endTime"]}", room: "{c["room"]}" }},\n'
        )
    f.write("];\n")

print(f"SUCCESS! Extracted {len(courses)} classes")
print("All courses:")
for c in courses:
    print("{"+f' code:"{c["code"]}",classNo:"{c["classNo"]}",name:"{c["name"][:40]:40}",weekday:{c["weekday"]},startTime:"{c["startTime"]}",endTime:"{c["endTime"]}",room:"{c["room"]}"'+"},")
