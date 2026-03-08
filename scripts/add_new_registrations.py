#!/usr/bin/env python3
"""
Script to add new registration data with events and workshops
"""
import json
import csv
from pathlib import Path

# New data from user (parsed)
new_data_raw = """Ranjhani. NR|iammeranjnr@gmail.com|8838132006|Saranathan College of Engineering
Raj kumar|raj16092007@gmail.com|9025175386|Saranathan college of Engineering
Himanshu Kumar|mr.himanshuthakur.in@gmail.com|9155220019|National institute of technology, tiruchirapalli
Floramary|floramarypathinathan366@gmail.com|7904554295|Shanmugha Arts, Science, Technology & Research Academy
Tivagar A|tivagar40@gmail.com|6379848284|Saranathan college of engineering
Nt Obito|oontguruvaran@gmail.com|6380683579|Saranathan college of Engineering Trichy
Induja N|nilavinmozhi@gmail.com|6374743157|NITT
Meyyappan|malarmeyy@gmail.com|8428307214|Saranathan college of engineering trichy
Prithish|prithish1908@gmail.com|8754319116|Saranathan College of Engineering
Aashay Vibhas|aashay.vibhas2005@gmail.com|9241126577|Nit Trichy
SURESH KRISHNA R|sureshkrishnar05@gmail.com|8015481406|Bharathidasan university
Ashwin Kumar|ashwinkumar9040404@gmail.com|8925014863|Sri Manakula vinayagar engineering college
vikhyat saini|vikhyatsaini95@gmail.com|8826834969|SRMIST Tiruchirappalli
Rahasya Pandey|rahasyapandey@gmail.com|8849391872|SRM UNIVERSITY
Riddishre E|riddishre@gmail.com|9384759131|SRM INSTITUTE OF SCIENCE AND TECHNOLOGY,TIRUCHIRAPPALLI
Chiraagg Sharma|chiraaggsharma0477@gmail.com|9316782914|Srm Trichy
Gokulraj Gopalakrishnan|gokulsundarges@gmail.com|6381721560|Anjalai Ammal Mahalingam Engineering College, Kovilvenni.
Anbukrishnan|reddyanbukrishnan1206@gmail.com|9313048567|Arunai Engineering College
Ponvannan M|ponvannan.m2325@gmail.com|8608612325|SRM MADURAI COLLEGE FOR ENGENEERING AND TECHNOLOGY
Sandhiya G|sandhiyagunasekaran64@gmail.com|9384423450|Anjali Ammal mahalingam engineering College
VIBUSHINI J R|vibushinivibushini@gmail.com|9344143282|SRM Madurai college for engineering and technology
Pavithran S|pavithran1562006@gmail.com|9962723573|Anjalai ammal Mahalingam engineering college
bhuvanakumar|bhuvanakumar323@gmail.com|8015772812|Anjalai Ammal mahalingam engineering college
WINSON ARAVINTH RAJ C|winsonaravinthraj@gmail.com|7904076807|PARISUTHAM INSTITUE OF TECHNOLOGY & SCIENCE, THANJAVUR
DHANAPRIYA N|dhanapriya825@gmail.com|8825885026|Arunai Engineering college
Sachin|sachinsinghrajpurohit10@gmail.com|9030274594|SRM TRICHY
Praveen Yadav|praveen3coc@gmail.com|9328390200|SRM TRICHY
Hanley David|hanleydvd@gmail.com|9633908329|Srm ist trichy
Zeyad Khan|khanzeyad49@gmail.com|8090802507|Srm trichy
Kaniti Anita|kanitianita09@gmail.com|7815916445|SASTRA DEEMED UNIVERSITY
Gobega S|gobegas454@gmail.com|7418737029|SASTRA Deemed University
Santhoshi S|127156145@sastra.ac.in|7810052107|Sastra University
Sree Vidya G|128158051@sastra.ac.in|9385643244|Sastra Deemed University
Shruthilaya J S|shruthihp1702@gmail.com|9789472108|SARANATHAN COLLEGE OF ENGINEERING
AKHIL SANDEL|akhilsandel440@gmail.com|8219654403|Srm trichy
Mohit Katal|mohitkatal58@gmail.com|7780841148|Srm trichy
Bhavya Kumawat|bhavyakumawat001@gmail.com|8290424815|Srm trichy
Tejas Bawankar|tejasbawankar2407@gmail.com|7249337367|Srm trichy
Himanshu Yadav|manjeeta083@gmail.com|9306287161|SRM Trichy
Mahesh Rajpurohit|mahesh1008purohit@gmail.com|9442277305|SRM Institute Of Science And Technology
Kavi Bharathi|kaviiitjee25@gmail.com|6380376737|NATIONAL INSTITUTE OF TECHNOLOGY TIRUCHIRAPPALLI
PADMA PRIYA V|padmapriya0819@gmail.com|8438405488|ANJALAI AMMAL MAHALINGAM ENGINEERING COLLEGE
Yamuna T|yamunathangamani9306@gmail.com|8903452199|Anjalai Ammal Mahalingam Engineering College
Ramkumar|ramkum188731@gmail.com|7871747832|Anjali ammal mahalingam engineering College
SAI SHASHANK PEDAPATI|saishashankpedapati@gmail.com|8925836316|Bharathidasan University
Miriam Grace|miriam23grace@gmail.com|8220254118|Solamalai college of Engineering
23Z306 - ANANYA R S|23z306@psgtech.ac.in|6382063280|PSG COLLEGE OF TECHNOLOGY
Harini Lakshmanan|harinilaksh3@gmail.com|8438536371|Saranthan college of engineering
PRIYADHARSHINI R|dharshinipriya221206@gmail.com|9360788268|SRM TRP ENGINEERING COLLEGE
Jeevika C|jeevika3114@gmail.com|8610426172|SRM Madurai College for Engineering and Technology
Logapriya S|logapriyaselvam213@gmail.com|9385797305|Dhanalakshmi Srinivasan University
Srinithi Meenakshi G|srinithimeenakshi22@gmail.com|9789361245|Sastra Deemed University
Nickson|sujithnickson7@gmail.com|9443327618|Saranathan college of engineering
Sanjay Deva V|deva19112005@gmail.com|8148588123|SRM MADURAI COLLEGE FOR ENGINEERING AND TECHNOLOGY
MOUNESH M|mounesh96290@gmail.com|9629044790|SRM MADURAI COLLEGE FOR ENGINEERING AND TECHNOLOGY
Amritha Sri|amrithasri007@gmail.com|8072065824|SRM Institute Of Science And Technology
R.RAJALAKSHMI|rajalakshmiravi3434@gmail.com|8072040877|MIET ENGINEERING COLLEGE
Vantrina John Britto|vantrinajohn@gmail.com|7200287717|Saranathan College of Engineering
Jeevitha R|jeevithar2810@gmail.com|9629188532|Dhanalakshmi Srinivasan University
SARVEPALLI AUDI SIVA BHANUVARDHAN|sarvepalliaudisivabhanuvardhan.set2023@dsuniversity.ac.in|9392630211|DHANALAKSHMI SRINIVASAN UNIVERSITY
Hari Priya|uniquehp19@gmail.com|7010371116|Sudharsan Engineering College
Keerthana.Aarul|keerthana2007@gmail.com|6380441868|Dhanalakshmi Srinivasan university , Trichy
Madhumitha N|madhumitha0379@gmail.com|9342790650|DHANALAKSHMI SRINIVASAN UNIVERSITY, TIRUCHIRAPPALLI
Roshan P|roshanr29969@gmail.com|8668113654|Indra ganesan college of engineering Trichy
Poojashree|pooja0532005@gmail.com|9962735666|SRM Madurai college for engineering and technology
MOUNESHA . S|ks.kmounesha@gmail.com|8695456677|SRM TRP ENGINEERING COLLEGE
Monisa. R|monisarajavel10@gmail.com|8489328297|SRM TRP ENGINEERING COLLEGE
Manisha M|sasinithis007@gmail.com|6385765783|SRM TRP ENGINEERING COLLEGE TRICHY
Lalli|lallishalu2006@gmail.com|8925620451|SRM Madurai college for engineering and technology
Jessie Ance|jezianzpaul@gmail.com|8870196809|SRM Madurai College for Engineering and Technology
Yuthica Sudhakar|2006syuthica@gmail.com|9941011177|SRM Madurai College for Engineering and Technology
23Z370 - SREEHARINI GANISHKAA S|23z370@psgtech.ac.in|9486465000|PSG College Of Technology
Lilly|lillyanj2006@gmail.com|7397553012|Anjalai ammal Magalingam Engineering college
NILANI G|nilanig7@gmail.com|6385156509|SRM TRP ENGINEERING COLLEGE
Sandhiya B|sandhiyabaskar704@gmail.com|8667344967|Anjalai Ammal Mahalingam Engineering College
POTHURAJU YASWANTH KALYAN|kalyanpothuraju1919@gmail.com|8520966488|DHANALAKSHMI SRINIVASAN UNIVERSITY
JANGITI SRI HARI|sri.hari69sri.hari@gmail.com|6300859394|Dhanalakshmi Srinivasan university
Pragadesh S|pragadesh.shan@gmail.com|8300067239|Anjalai Ammal Mahalingam Engineering College
Rahul Ganapathy|lalli132006@gmail.com|9342552966|SRM Madurai college for engineering and technology
Prince Chaurasiya|princechaurasiya7600@gmail.com|7294076871|SRM Institute Of Science And Technology
Ayaan|ayaan358374@gmail.com|6202588364|Srm institute of Science and Technology
Murshida Shirin S|murshidasabjan@gmail.com|9444153695|Anjalai Ammal Mahalingam Engineering College
Madhusha.s|srmadhusha05@gmail.com|6381264302|Solamalai College of engineering
HARSHINI BALA S|harshithemajestic@gmail.com|7871469410|Anjali Ammal Mahalingam Engineering College
Ganesh Kumar|ganeshkumar69500@gmail.com|8148080436|Indra Ganesan college of engineering trichy
Sreeman|sreeman252008@gmail.com|9487311145|Srm institution of science and technology trichy
Manikkavel S|manikkavelsellappillai@gmail.com|8056614862|Indra Ganesan college of engineering
Rakshana.s|rakshanaraksh87@gmail.com|8754110465|Solamalai college of engineering
Sasi Kumar|chellanpalanivelchellan@gmail.com|8973629298|Indra Ganesan college of engineering Trichy
Raji Malaisamy|rajimalaisamy12@gmail.com|6376729736|Solamalai college of engineering
Bikash Gupta|bikashgupta2079@gmail.com|9798167587|SRM institute of science and technology
Rupesh Thakur|rt983122@gmail.com|9304380290|SRM Institute Of Science And Technology
ATHISH PRANAV|athishpranav2@gmail.com|9791224969|PSG COLLEGE OF TECH
S SANJEEV|23z361@psgtech.ac.in|7418695999|Psg college of technology
Jayamalar|jayamalarjx2006@gmail.com|8870890186|Parisutham Institute of Technology and Science
Dhiraj Kushwaha|dhirajkush012@gmail.com|7319613895|SRM Institute Of Science and Technology
SUPRIYA M P|24104162@drngpit.ac.in|7373620356|Dr.N.G.P INSTITUTE OF TECHNOLOGY
Niranjana|niranjana2875@gmail.com|6383090622|Solamalai college of engineering
Yogita|yogszz11.11@gmail.com|9994766692|SRMIST Trichy
M L KUSSHAL GOWDA|kusshalgowda6@gmail.com|8310860237|National institute of technology Tiruchirappalli
Bhargavi A.R|bhargavi2007raghu@gmail.com|9943559113|Anjalai ammal mahalingam engineering college
Harini|harinimurali@gmail.com|8015971499|Anjalai ammal Mahalingam engineering college
Pravin Kumar|pravinkumar01.tech@gmail.com|8778185791|Kamaraj college of engineering and technology
Narendra Prakash A|narentg2007@gmail.com|6374972634|Dhanalakshmi Srinivasan college of engineering and technology, Mamallapuram, Chennai
Vijay Anand.S|vijayanand102006@gmail.com|8778241576|Dhanalakshmi Srinivasan College of Engineering and Technology
Varsha V|varshavenkateshan28@gmail.com|9655826160|SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
Dana Darthy|112danadarthy@gmail.com|9659058367|SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
janani N|jananinarayanan5@gmail.com|8248705132|SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
Rashiyasri Senthil kumar|ruchierash7@gmail.com|9345532636|SRM Institute of Science and technology
Vaishnave .M|vaishnavemurugesan113@gmail.com|7530025101|SRM institute of science and technology
A RAJ P|pa.anantharaj.mdu@gmail.com|9443644646|NIT Trichy
Sowmiya K|sowmiyadhanu67@gmail.com|9942814198|Dr. N. G. P. Institute of Technology
Keerthana K|keerthanakarthi193@gmail.com|9361056899|Dr NGP Institute of Technology
Abiraame Kannan|abiraamekannan8@gmail.com|6379267734|Sathyabama University
Balachandar R|balachandar.rv205@gmail.com|8903196625|Anjalai ammal mahalingam engineering college
Sudharshinisudharshini22102007@gmail.com|8754235645|Srm University
Anshu Prasad Sarraf|satuwasarraf850@gmail.com|7569096514|SRM UNIVERSITY
Jehojacsy J|jehojacsy36@gmail.com|8807836948|PSGR KRISHNAMMAL COLLEGE FOR WOMEN
SNIRMAL KUMAR K|24z464@psgtech.ac.in|9500575064|PSG College Of Technology
Hari Haran|s.hariharansss21@gmail.com|6374361791|Anjalai Ammal Mahalingam Engineering College"""


def parse_new_data():
    """Parse the new data into structured format"""
    entries = []
    for line in new_data_raw.strip().split('\n'):
        parts = line.split('|')
        if len(parts) >= 4:
            entries.append({
                'name': parts[0].strip(),
                'email': parts[1].strip().lower(),
                'phone': parts[2].strip(),
                'college': parts[3].strip()
            })
    return entries


def load_existing_data():
    """Load existing registration data"""
    json_path = Path('backend/data/registration_data.json')
    with open(json_path, 'r') as f:
        return json.load(f)


def load_csv_data():
    """Load CSV data to check for existing workshops/events"""
    csv_path = Path('backend/data/user_details_report.csv')
    csv_data = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['Email'].strip().lower()
            csv_data[email] = {
                'workshops': [w.strip() for w in row['Workshops'].split(',') if w.strip()],
                'events': [e.strip() for e in row['Events'].split(',') if e.strip()],
                'year': row['Year'].strip() if row['Year'].strip() else None,
                'gender': row['Gender'].strip() if row['Gender'].strip() else None,
                'summer_internship': row['Summer Internship'].strip() if row['Summer Internship'].strip() else 'No'
            }
    return csv_data


def main():
    print("Loading existing data...")
    existing_data = load_existing_data()
    csv_data = load_csv_data()
    new_entries = parse_new_data()

    # Create email lookup for existing data
    existing_emails = {entry['email'].lower() for entry in existing_data}

    # Get next ID
    next_id = max(entry['id'] for entry in existing_data) + 1

    added_count = 0
    updated_count = 0

    print(f"\nProcessing {len(new_entries)} new entries...")
    print(f"Starting ID: {next_id}")

    for new_entry in new_entries:
        email = new_entry['email']

        # Check if email already exists
        if email in existing_emails:
            # Find and update existing entry
            for entry in existing_data:
                if entry['email'].lower() == email:
                    # Check CSV for additional data
                    if email in csv_data:
                        csv_info = csv_data[email]
                        # Add workshops and events if not already present
                        for workshop in csv_info['workshops']:
                            if workshop and workshop not in entry['workshops']:
                                entry['workshops'].append(workshop)
                        for event in csv_info['events']:
                            if event and event not in entry['events']:
                                entry['events'].append(event)
                        updated_count += 1
                    break
        else:
            # Add new entry
            new_record = {
                'id': next_id,
                'name': new_entry['name'],
                'email': email,
                'phone': new_entry['phone'] if new_entry['phone'] else None,
                'college': new_entry['college'],
                'year': None,
                'gender': None,
                'summer_internship': 'No',
                'workshops': [],
                'events': [],
                'city': ''
            }

            # Check CSV for additional data
            if email in csv_data:
                csv_info = csv_data[email]
                new_record['workshops'] = csv_info['workshops']
                new_record['events'] = csv_info['events']
                new_record['year'] = csv_info['year']
                new_record['gender'] = csv_info['gender']
                new_record['summer_internship'] = csv_info['summer_internship']

            existing_data.append(new_record)
            existing_emails.add(email)
            next_id += 1
            added_count += 1

    # Save updated data
    output_path = Path('backend/data/registration_data.json')
    with open(output_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

    print(f"\n✓ Added {added_count} new registrations")
    print(
        f"✓ Updated {updated_count} existing registrations with events/workshops")
    print(f"✓ Total records: {len(existing_data)}")
    print(f"✓ Saved to {output_path}")


if __name__ == '__main__':
    main()
