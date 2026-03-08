#!/usr/bin/env python3
"""
Script to add Code Combat event to participants
"""
import json
from pathlib import Path

# New data for Code Combat event
code_combat_data = """Jeevan R P	jeevanrp2006@gmail.com	8072406233	Achariya College Engineering Technology
Shanmugasundaram G	shanmugasundaram2023@gmail.com	8248452042	saranathan college of Engineering
Navinkumar G	naveenganesan0702@gmail.com	8122071980	Achariya College Of Engineering Technology
Bunni Ranadeesh	bunni.ranadeesh4751@gmail.com	12345647890123	dsf
Reimann	ranabhai4751@gmail.com	9000232210	NIT Trichy
jey	firefoxguy777@gmail.com	9360877548	NIT Trichy
Hari Kumar A	harikumar3868@gmail.com	8525059820	NIT Trichy
Sudharsan M	sudharsan.mgm17@gmail.com	8610767397	Sona College of Technology, Salem
Archi Shah	shaharchi868@gmail.com	9316544868	Nit Trichy
ranjith	ranjithsankar108@gmail.com	9363617203	Achariya college of engineering technology
Abdul Ajees P	ajees4967@gmail.com	7397655147	SARANATHAN COLLEGE OF ENGINEERING
Raj kumar	raj16092007@gmail.com	9025175386	Saranathan college of Engineering
Gireesh A	gireeshnitt@gmail.com	9840725886	NIT Trichy
Kevin Kumar	kevinkumar2029@gmail.com	8807190644	Nit Trichy
Gopichand V S	vsgopibhanu@gmail.com	8015447216	Nit trichy
AVILASH S	savilash25@gmail.com	9360312860	SARANATHAN COLLEGE OF ENGINEERING
Pranava Mohan	pranavamohan321@gmail.com	9345103835	NIT Trichy
Ramanathan R	ramanathan87782@gmail.com	6379753742	MAM college of engineering
Vikash Singh	vikashsingh.nitt@gmail.com	7004340476	National Institute of Technology Tiruchirappalli
Akshat Goyal	akshatgoyal.rpr@gmail.com	9111306300	NIT Trichy
Abhishek Antony	abhishekantony777@gmail.com	6369878867	Achariya College of Engineering Technology
Manthan Gaur	manthangaur7777@gmail.com	9462327111	NIT Trichy
Devansh Shukla	devansh9892@gmail.com	8652395330	NITT
Romit Ranjan	ranjanromit35@gmail.com	8235037408	NIT Trichy
Dharshini S	dharshusenthil2006@gmail.com	6379296697	Kongunadu College of Engineering and Technology
Rahul	abr14022007@gmail.com	9566646236	Kalasalingam university,srivilliputhur
Vijay SA	ivijaysa@gmail.com	7904319369	Saranathan College of Engineering
VARSHA VARRDHINI.N	cse271114@saranathan.ac.in	9363974326	Saranathan College of Engineering
CHANDRAMOHAN SARAVANAN	chandramohan040406@gmail.com	9843610806	Thiagarajar College of Engineering
ANSHUMAN NARENDRAJIT SINGH	anshumannarendrajitsingh@gmail.com	8658159749	NIT TRICHY
Rashmi Ranjan Sahoo	rsahoorashmi@gmail.com	6370584635	Nit trichy
Pradeep	praddyp7@gmail.com	9123544521	Sudharsan Engineering College
Shreyan Sadhukhan	neelshreyan2004@gmail.com	6289971889	SRM IST, Trichy
kaashnii j	jkaashnii@gmail.com	9342412312	SRM University
Thomas Amala Heringston	thomas.a10242@gmail.com	8072773748	Saranathan college of engineering
Thameej Ahamed	thameejahamed73@gmail.com	6369594151	SRM MADURAI COLLEGE FOR ENGINEERING AND TECHNOLOGY
R.Balaganesh	rbalaganesh2307@gmail.com	6379481844	Achariya College of Engineering Technology
Bala Murugan	bala72102@gmail.com	7449188616	Saranathan college of engineering
Harish R	harishravi2186@gmail.com	8056426055	Saranathan college of engineering
SREE SAI DRONADULA	sai.iirs.isro@gmail.com	6362786797	SASTRA DEEMED UNIVERSITY
LOGESHWARAN. A	cse271062@saranathan.ac.in	9786063434	saranathan college of engineering
Komal	komal.0x22@gmail.com	9877359957	SRM University
Pratik Kumar	pratikkumar060207@gmail.com	7992308648	NIT TRICHY
prasanna b	pb2302131@gmail.com	6383824530	SRM Valliammai Engineering College
SnowMan	epiccgamer18@gmail.com	8369612047	National Institute of technology Tiruchirappalli
Tanmay Sagar	sagartanmay2004@gmail.com	9373367754	NIT Trichy
Harish Kumar	2417harishkumar@gmail.com	8148305250	Saranathan College of Engineering
Ramya	ramyaashok715@gmail.com	9342837512	Saranathan college of engineering
Aakash P	aakashp31102005@gmail.com	9344522789	Government College of Engineering, Thanjavur
Nimish R	nimishr993@gmail.com	9688414284	Saranathan college of engineering
Varnapriyaa	priyasurya2826@gmail.com	8838662251	SRM Institute of science and technology
Rithanya Prabhu	rithanyaprabhu12@gmail.com	7010442051	SRM Institute of science and technology
ROJAR ARO	ra0497@srmist.edu.in	9080709504	TRICHY SRM
pavitha kannan	pavitha187@gmail.com	8807172697	Srm university
Hari Priya A	aharipriya019@gmail.com	8760006414	K Ramakrishnan College Of Engineering
Harini Parameswaran	hariniparameswaran600@gmail.com	9600366692	Saranathan college of engineering
Janani G	janani05gopal@gmail.com	8220796312	Sri Krishna College Engineering and Technology
VINO PABIYANA L	vinopabiyana.l@gmail.com	7397679057	SSM Institue of Engineering and Technology
RITIKA MUTHUKUMAR	ritikamuthukumar07@gmail.com	7708900545	SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
Harish Deishmuk	karthikeyanharish269@gmail.com	8056770879	SRM Institute of Science and Technology
Madhu Parameswari Ganesan	madhuparameswari6572@gmail.com	7708927851	Sastra Deemed to be University , Thanjavur
Shravan Shriram S	128003243@sastra.ac.in	9790009584	Sastra University Thanjavur
VIDYASAAGAR S	vidyasaagar.al23@krct.ac.in	8148010091	K Ramakrishnan College of Technology
Jacinth	jacinth485@gmail.com	8778168712	SRM MCET
HARINI K	hariharinisangraja@gmail.com	6369555890	K RAMAKRISHNAN COLLEGE OF ENGINEERING
Sakthi Kannan	sakthikannan9793@gmail.com	9360721052	SRM TRP Engineering College
Surya	smileyyt06@gmail.com	8925339718	Sudharsan Engineering College
MR. M S K MAHESH	maheshmsk2006@gmail.com	8489453684	SRM Madurai College For Engineering And Technology
Aanandha Ruban	rubanmrk@gmail.com	9345558985	SRM Madurai College for Engineering and Technology
Dhavaputhalvi	dhavaputhalviramesh@gmail.com	8925419957	Government College of Engineering Srirangam
Reegan Ferdinand k	reeganferdinandk0710@gmail.com	9025474684	Sri Eshwar College Of Engineering
Surya	newbmwjourney@gmail.com	8925339718	Sudharsan Engineering College
Vasanth Sivakumar	vasanthsivakumar10@gmail.com	8870445237	SNS College of Technology
vivin raj vivin raj	vivinrajvivinraj0@gmail.com	9629341286	Srm ist
Mayura Priyan G	mayurapriyan21@gmail.com	9042663721	Sri krishna college of technology
MOHAMEDSABERALI O	gowsatholi@gmail.com	8973314861	SRI KRISHNA COLLEGE OF TECHNOLOGY
Kavya	kavyap2207@gmail.com	9360014558	KONGU ENGINEERING COLLEGE
SIVANARAYANAN M	snsiva854@gmail.com	9344702577	Achariya college of engineering technology
MOHAMED RIZWAN R	mohamedrizwan4518@gmail.com	9360496365	ACHARIYA COLLEGE OF ENGINEERING TECHNOLOGY
Meganan.v	megananv06@gmail.com	7397715455	Achariya college of engineering technology
Saindhavi S A	saindhavi2546@gmail.com	7010742578	Government college of engineering Srirangam
Prasath S	saprasath15@gmail.com	8825918573	Achariya College of Engineering Technology
Hari Vishalini	itzmeharivishalini007@gmail.com	9193450690	Srm Madurai college for engineering and technology
Sachin	sachinsinghrajpurohit10@gmail.com	9030274594	SRM TRICHY
Raj Kumar	rajk5669291@gmail.com	9486163746	achariya college of engineering technology
Harini M	harinimurugesan14@gmail.com	9345304624	SRM Madurai College For Engineering And Technology
logitha Swamy	logithaswamy@gmail.com	7904898068	SRM Madurai college for engineering and technology
T.k.g Samni	tkgsamni36@gmail.com	9080485140	SRM Madurai college for engineering and technology
Gokularam M	gokularamrm@gmail.com	8870213343	SRM MADURAI FOR ENGINEERING AND TECHNOLOGY
Balaji 2006	balaji2006raj@gmail.com	9363979850	Saranathan College of engineering Trichy
Deva Dharshini	deva300806@gmail.com	9443253535	SARANATHAN COLLEGE OF ENGINEERING
SIVASUBRAMANIYAN K	sivakarnan03@gmail.com	9361645324	Achariya college of engineering technology
Sugumar s	sugu28812@gmail.com	7449089835	Dhanalakshmi srinivasan University
Dharshini Marimuthu	dharshmarimuthu1509@gmail.com	8248649196	Srm institute of science and technology
Prasanth Narayanan V S	prasanthjoueur@gmail.com	8015928461	SRM madurai college for engineering and technology
Tejas Bawankar	tejasbawankar2407@gmail.com	7249337367	Srm trichy
Sivaranjani	aranjanisiva8@gmail.com	9025270016	K.Ramakrishnan college of technology
Kaviin	kaviin360@gmail.com	8608209705	NIT Tiruchirappalli
Rajesh E	eerajesh545@gmail.com	8098518262	Achariya college of engineering technology
Ruban Ruban	rubanchakravarthy05@gmail.com	6374079306	Srm madurai
Harish	harishpixelmlbb@gmail.com	6379519241	sudharsan engineering college
Jayasakthi K R	jayasakthiramkumar@gmail.com	9050518863	SRM Madurai College for Engineering and Technology
Karthick Babu A V	karthickrakesh4@gmail.com	9787097424	SRM Madurai College for Engineering and Technology
Faazil Ahamed M	faazil2006@gmail.com	9361187872	SASTRA UNIVERSITY
Karthikeyan K	karthikumar0812@gmail.com	6374450242	Government College of Technology
Mukesh N	indranatraj2@gmail.com	7868907074	Puducherry Technological University
JEYALAKSHMI SHANMUGAM	jeyashanmugam35@gmail.com	9865371144	PSG college of arts and science
Ruthreswaran K	ragaruthra@gmail.com	9597314692	Puducherry Technology University
Palraj J	palrajj6107@gmail.com	9952681449	Anna University Regional Campus Tirunelveli
Atchaya K	atchayakumar888@gmail.com	7010882975	National institute of technology tiruchirappalli
Ashish Kumar	ashishkr2220@gmail.com	9905130737	NITT
IRUDHAYA ALBERT A	albert26112005@gmail.com	9442466926	SRM Madurai College for Engineering and Technology
Mohammed Parvez Y	mohammedparvezofficial@gmail.com	8667079233	Anna University Regional Campus, Coimbatore
yogachandra moorthy	yogachandramoorthypalanivel@gmail.com	8940442702	SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
Kevin Thangam	kevinthangamjacob19@gmail.com	9944459204	Dhanalakshmi srinivasan university
R. PRIYADHARSAN	rpriyadharsan49@gmail.com	9361077348	Dhanalakshmi Srinivasan University
Harini.B	harinib110@gmail.com	9514263244	Dhanlakshmi srinivasan university
Srirama Narayanan S	sriramnova2006@gmail.com	7598141143	Anna university regional campus Tirunelveli
Abdul Basith	05abdulbasith@gmail.com	9363586637	Dhanalakshmi Srinivasan university
Maha vishnu	dhavamanig0519@gmail.com	6381046976	PAAVAI ENGINEERING COLLEGE
Harshath Magesh	harshathmagesh3@gmail.com	9360731378	SNS COLLEGE OF TECHNOLOGY
Santhosh K	sxndyofficixl01@gmail.com	8903409173	Achariya college of engineering technology
Jeyadharshni	jeyadharshni75@gmail.com	9385833800	Dhanalakshmi srinivasan University
Vimala Dharshini	kvimala182006@gmail.com	8870378208	Dhanalakshmi Srinivasan university
Madhan Kumar S	madhanshankar2006@gmail.com	9345043376	Anna University Regional Campus Tirunelveli
Nabeela Begum	nabeelabegum1706@gmail.com	8015014517	Dhanalakshmi Srinivasan university
Akash	mv.akash2008@gmail.com	7569870717	National institute of technology Tiruchirappalli
Sumith Kumar	kumarsumith708@gmail.com	8148804915	Dr NGP INSTITUTE OF TECHNOLOGY
Loakesvaraan	loakesvaraanmeenal@gmail.com	8248585339	Karpagam Institute of Technology
Sayee Naveen J S	sayeenaveenjs@gmail.com	6382905380	SRM MCET
jasitha Palanivel	jasithapalanivel879@gmail.com	8248414558	Dhanalakshmi Srinivasan collage of Engineering and technology
Len_Lenin _	leninlendoo07@gmail.com	8122892988	SRM IST TRICHY
Logesh N	logeshlogesh07082004@gmail.com	7867949312	The Gandhigram Rural Institute (Deemed To Be University), Dindigul - 624302
Divyadharshini M	divyadharshinind.1020@gmail.com	7397142818	Dr. N. G. P. Institute of Technology
Bala Prashidha M	balaprashidha@gmail.com	6381734393	Dhanalakshmi Srinivasan university
SARAVANA RAJESH	saravanarajesh07@gmail.com	9566156201	PSG college of arts and science
Saravanan M	saravananm2119@gmail.com	9842820025	Achariya college of engineering technology
YOUSUF KHAN	yousufkhanashik7860@gmail.com	9080903305	Sri Krishna College Of Technology
TOANISHWAR S	727824tuad245@skct.edu.in	9025620089	Sri Krishna College of technology
SANJAY SANJAY	ssanjay75682@gmail.com	9342044193	KRCE
YOUSUF KHAN P	727824tuad261@skct.edu.in	9080903305	Sri Krishna College Of Technology
SANJAY S	727824tuad216@skct.edu.in	9363730484	Sri Krishna College of Technology
Joe Clement E	researchworker8@gmail.com	7904712809	Saranathan College Of Engineering
Adhithi	adhithiarun2007@gmail.com	8883236667	Dhanalakshmi Srinivasan university Trichy
Saraal	saraalsathiyanathan@gmail.com	9597621044	K Ramakrishnan college of engineering
AKASH	jagathambalcranes@gmail.com	9597008499	anajalai ammal mahalingam engeneering college
SANJAY SS	727824tuad259@skct.edu.in	7418972999	Sri Krishna College Of Technology
VAMSIRIDDHARA SYLESH V R R	727824tuad249@skct.edu.in	7904850898	Sri Krishna College Of Technology
SIVAPRASANTH K	727824tuad224@skct.edu.in	8122277927	Sri Krishna College Of Technology
Priyanka V	vengatachalam2007@gmail.com	7397477063	K.Ramakrishan college of engineering
SREENATH S	727824tuad229@skct.edu.in	9345390242	Sri Krishna College Of Technology
Dev N	devnfordailyuse@gmail.com	9892089893	Nit Trichy
Avi	avi032904@gmail.com	6287853100	NIT TRICHY
Piramila S	piramilasugumaran@gmail.com	6385133191	K RAMAKRISHNAN COLLEGE OF ENGINEERING
Abarna S	abarnasudarolian2005@gmail.com	6382625447	University college of engineering Tindivanam
S. Sudharsan	sudharsansankar739@gmail.com	9585255459	University College of Engineering Tindivanam
SIVALINGA PERUMAL N	siva948875@gmail.com	9345449793	University college of engineering tindivanam
Gayathri S	gayusekar0806@gmail.com	8610789351	University college of engineering Tindivanam
KALIMUTHU V	kalimuthu99909@gmail.com	6369950186	UNIVERSITY COLLEGE OF ENGINEERING TINDIVANAM
Madhumitha S	smadhumitha218@gmail.com	8667560031	University college of engineering tindivanam
Aditya Kumar	adityakumar071106@gmail.com	9571214368	National Institute of Technology Trichy
Parth Malguzar	parthmalguzar@gmail.com	7225087570	NITT
J preetha priyadharshini	jpreethapriyadharshini@gmail.com	8870531192	Dhanalakshimi srinivasan university
Mirudhula V	mirudhula147@gmail.com	9363836746	Dhanalakshmi Srinivasan university
Santhiya	santhiyapushparaj137@gmail.com	8124332910	K.Ramakrishnan college of Engineering
Kavin Prescilla p	pkprescilla251107@gmail.com	6385557583	Dhanalakshmi Srinivasan university
Vimala P	vimala29.p@gmail.com	8438474352	Dhanalakshmi Srinivasan university
Divyansh Joshi	divyanship19@gmail.com	9354548817	Nit trichy
Sathya M	sathyamurugesan0546@gmail.com	9500548895	DHANALAKSHMI SRINIVASAN ENGINEERING COLLEGE, PERAMBALUR
THIRISHA V	mukeshthrisha283@gmail.com	8610473956	Dhanalakshmi Srinivasan Engineering College
Sindhiya Abineswari	sindhiya0311@gmail.com	7449076911	SARANATHAN COLLEGE OF ENGINEERING
Divakar Kumar. B.V	vikashshah2916@gmail.com	9572402916	KS Rangasamy College of arts and science
Sivalinga Perumal N	sivamaths9345@gmail.com	9345449793	UCET
NITHISH KUMAR SARAVANAN	nithishkumarsaravanan8@gmail.com	8015413019	Saranathan college of engineering
Hirthik Balaji C	hirthikbalaji2006@gmail.com	8248827972	Amrita vishwa vidhyapeetham
JAWAHAR K	jawahark.ec24@krct.ac.in	8939801248	K.Ramakrishnan collage of technology
Tejaswini S	stejaswini329@gmail.com	7204322400	SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
Vaishnavi	vaishnavi070908@gmail.com	8438046623	Dhanalakshmi Srinivasan University-samayapuran
DICSON MOSES D	dicsonmoses02@gmail.com	9751956315	K.RAMAKRISHNAN COLLEGE OF TECHNOLOGY
Venkat ramana	venkatramana06062008@gmail.com	9100095069	nit trichy
Rohak	rohakedagotti@gmail.com	8074981784	Nit Trichy
Sanket Yadav	sanketyadav2411@gmail.com	9309285903	NIT Trichy
Mohammed Aasif	aasifibrahim04@gmail.com	7305948488	National Institute of Technology Tiruchirapalli"""


def parse_code_combat_data():
    """Parse the Code Combat participant data"""
    entries = []
    for line in code_combat_data.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 2:
            entries.append({
                'name': parts[0].strip(),
                'email': parts[1].strip().lower()
            })
    return entries


def main():
    print("Loading existing registration data...")
    json_path = Path('backend/data/registration_data.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Parse Code Combat participants
    code_combat_participants = parse_code_combat_data()

    # Create email lookup
    email_to_entry = {entry['email'].lower(): entry for entry in data}

    added_count = 0
    not_found = []
    already_has = []

    print(
        f"\nProcessing {len(code_combat_participants)} Code Combat participants...")

    for participant in code_combat_participants:
        email = participant['email']

        if email in email_to_entry:
            entry = email_to_entry[email]

            # Check if already has the event
            if 'Code Combat' in str(entry.get('events', [])):
                already_has.append(participant['name'])
            else:
                # Add the event
                if 'events' not in entry:
                    entry['events'] = []
                entry['events'].append('Code Combat')
                added_count += 1
        else:
            not_found.append(f"{participant['name']} ({email})")

    # Save updated data
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Added 'Code Combat' event to {added_count} participants")
    print(f"✓ {len(already_has)} participants already had the event")

    if not_found:
        print(f"\n⚠ {len(not_found)} participants not found in database:")
        for name in not_found[:10]:  # Show first 10
            print(f"  - {name}")
        if len(not_found) > 10:
            print(f"  ... and {len(not_found) - 10} more")

    print(f"\n✓ Total records: {len(data)}")
    print(f"✓ Saved to {json_path}")


if __name__ == '__main__':
    main()
