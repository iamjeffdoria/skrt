import csv

# Function to write a row to the CSV file
def write_row(writer, row_values):
    writer.writerow({
        "#": row_values[0],
        "Date Joined": row_values[1],
        "Student ID": row_values[2],
        "Full Name": row_values[3],
        "Course": row_values[4],
        "Major": row_values[5],
        "RFID #": row_values[6]
    })

# Main code
with open('student.csv', mode='w', newline='') as csvfile:
    fieldnames = ["#", "Date Joined", "Student ID", "Full Name", "Course", "Major", "RFID #"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Writing the first row
    write_row(writer, ["1", "3-25-1999", "151171810", "Charita Doria", "BSIT", "IT", "1234"])
    
    # Writing additional rows
    additional_rows = [
        ["2", "4-10-2000", "151171811", "Ariel Dela Hubkas Jr Et Al III", "BSCS", "Computer Science", "5678"],
        ["3", "5-15-2001", "151171812", "Vivien Demate Orion", "BBA", "Business Administration", "9012"]
        
        # Add more rows here if needed
    ]
    
    for row in additional_rows:
        write_row(writer, row)
