# Ring HE App

## Overview

The **Ring HE App** is a decentralized homomorphic encryption application where multiple members of a "ring" contribute encrypted data. The leader of the ring initiates the process by encrypting their data and passing it along the chain. Each member encrypts their own data and adds it to the rolling sum, which is continuously passed to the next member. Once the process completes, the ring leader decrypts the final sum and publishes the result. A video demo is below:




### Key Features:
- **Homomorphic Encryption**: Uses the Paillier cryptosystem to securely aggregate encrypted data.
- **Decentralized Workflow**: Each member contributes to the final result without knowing the intermediate sums.
Note that this does not address all the challenges with secure aggregation (such as robustness, secureity against global adversaries etc.). Furthermore, it is a quick prototype of how such a system can be built using SyftBox, a more secure version can be built using the full power of the SyftBox permissions system.

## How to Run the App

1. **Setup**:
   - Place your secret data in `private/secret.json`. Example `secret.json` file:

```json
{"data": 42}
```

2. **Run**:
   - Install the app: `syftbox app install snwagh/ring-he`
   - If you are the ring leader, initialize the computation by adding all participants (first participant is yourself) in `data.json` and place it in the specified folder. 
   
   
3. **Output**:
   - The final result will be published at `leader@openmined.org/api_data/ring-he/ring-he-result.json`. Example `ring-he-result.json` file:
```json
{"result": 42}
```



## Behind the Scene: How It Works

1. **Ring Leader Initialization**:
   - When the **ring leader** initializes the computaiton, they generate a set of Paillier encryption keys which is a partially homomorphic encryption scheme.
   - They encrypt their secret data (stored in `private/secret.json`) thus starting the rolling sum of member's secret data, and pass the data to the next member in the ring (file `api_data/ring-he/data.json` in the next ring member's datasite).

2. **Ring Members**:
   - Each member of the ring waits to receive the `api_data/ring-he/data.json` file from the previous member.
   - When they receive the file, they encrypt their secret data (`private/secret.json`) and add it to the rolling sum. The public key for the encryption will be in the `data.json` file.
   - They then pass the updated sum to the next member in the ring.

3. **Ring Termination**:
   - Once the `data.json` file reaches the **ring leader** again, the leader decrypts the final aggregated sum and publishes it in the `api-data/ring-he/ring-he-result.json` file.



## Directory Structure

```plaintext
.
├── private/                    # Directory for storing private keys and secret data
│   └── secret.json             # File containing the user's secret data
│   └── *_key.json              # Leader will have the keys here
└── datasites/<email_id>/api_data/ring-he/
    └── ring-he-result.json     # Leader will publish this file containing the sum of all users 
```

## Ring Workflow

- **Keys**: Only the ring leader generates Paillier keys and shares the public key with all members via the `data.json` file.
- **Rolling Sum**: Each member encrypts their data and adds it to the rolling sum (`data.json`), passing it to the next member.
- **Decryption**: Only the ring leader can decrypt the final sum after all members have added their contributions.

## Example `data.json`

The ring will start with a `data.json` file in the `api_data/ring-he` folder of the ring leader. Example of the `data.json` file for initialization looks like: 

```json
{
  "participants": ["leader@openmined.org", "member1@openmined.org", "member2@openmined.org"]
}
```

an example of a `data.json` file for an intermediate state looks like: 
```json
{
   "participants": ["leader@openmined.org", "member1@openmined.org", "member2@openmined.org"],
   "public_key": {
      "n": "4462236161794885214579296631944927151864587369733549608928207478693020549524892283729905652332440605263124631550653362807011792144346970425518194424271634857049233630634123426855056399066233475071773661236466323786475345303157818969838194788332020226874137720876930917296301505649128236598124436515573627392842680526083825866735786085257663219270935016766539954481933337625606403466659305227386921064257854193792671813725819997241451263023432585519150584132257077047746827265173135430806559036609537415293621401353997485397982171635330300293219001153402228565902439117332101910251354586208087847879014305520357995283417047327139437776139404818623039349846345073178295139235828047401771831193496684563606583141177414492947035233195826583988041524796779267507192694231028961111819239154734415661727590176544121617695673762152139072101600753647844024964384317283681309053238360599949533036952240843214342295645594992533595591607"
   },
   "data": "612214972416158644690289333773218789194314678276761668567745735714499449526617534046234649305487206186295600101461425289761028648096351569620076992187954920381049162126821370295679634020251625524967416844490645075351813298003878735988080011592377376677271204081021974802153978278448584779182147940733792419917890654152366881083591987747911190064492622970792821498385806633710491482267699289528540626247296815288184634491225533593997245499710616724065657429782499569465155002360231758882028459031111436631697769445177346152972935213954632814592433922603708251761329179213094195776201475799918637467051829101008094182964294584454045603060278837634906713059523490779398695028638938237798617903205933694816682267498449083891077368569232276037955629250938807887337945784917178397574651120327650595657531484504864386624905297220263037434687230045901153182591135320035702273901106897064882803035057361550237942141548313977167695195671594859234744753940510146562696459682961890468518825213878278709176374550938041425700369489875415881898951511682117838464176997157291354412691150626383810840896041337839707172088543352614299146326498161512608313214184149790441295875735982852181240062867890039600384030626303273099292886720283938179714453664345502304831402244640806902078201142500582989038847643604224019969029448330383036393806000434337905546165813642037665132266073319081134432253313408608895086853028709483234194730745928913095476058621816302141457125386512505798475004824732728544269617350466783543938389600612162915272265440188040972271597223708754164260347172187770559807430626514396996379082795755964582998233481354020543145612104062375281210454788295954048781529392281797435597081214690480303984192742262729707599634389865984364657691963856260187632641086795910520158759247539660744592006606112181249110319854377607733715414873724441332068885049016"
}
```

## For Developers
Take a look at this video: 

https://github.com/user-attachments/assets/25e90f29-0324-4877-b99d-fa1560d6913f
