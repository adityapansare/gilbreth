# Gilbreth

## Setup

### Prerequisites

To run Gilbreth as intended, you will need the following:

> A machine running Ubuntu 18.04 OS, that can support CUDA >= 10.0.

### Install Darknet
1. Clone AlexeyAB's darknet repository into the deep_learning directory such that the root of the darknet repository is in the deep_learning directory. Do this by running
```
cd deep_learning
rm -rf darknet #remove any existing directories named darknet, alternatively, rename them
mkdir darknet
git clone https://github.com/AlexeyAB/darknet.git darknet
```
2. Follow the instructions in the darknet repository to build darknet for your system. In the end, you must have an executable file named darknet in the repository, such that the full path is `deep_learning/darknet/darknet`

### Set Up Cloud Vision
We use Google Cloud Vision API for our OCR operations. You therefore need to generate a token of your own for the Cloud Vision API. You can do this by following these instructions, and then storing the token in `ocr_module/gilbreth-token.json`

1. Go to the Google Cloud Console at https://console.cloud.google.com/.
2. Go to the marketplace and search for the Cloud Vision API.
3. If you're using it for the first time in the selected project, then click on enable API, otherwise click on Manage.
4. The next screen will show all API keys, OAuth client IDs and Service account associated with the API and the project. Press on create credentials.
5. This will let you create a new Service Account. After creating it, select the Key Type as JSON. Click the `create` button, and the JSON token will start downloading.

Once the token is downloaded and stored as `ocr_module/gilbreth-token.json`, install the python packages for Google Cloud Vision.
```
pip install google-cloud-vision protobuf google-api-core google-auth
```

### Set Up Open-CV (optional)
For running the 4-point perspective transform (only in the case of skewed flowcharts), you will need to install OpenCV for your device.

## Running the Program

In case of a skewed flowchart, straighten it using the 4-point perspective transform provided in deep_learning/preprocessing

Then run
```
python gilbreth.py <image path>
```

For example-
```
python gilbreth.py fc_dirs/flowcharts/Flowcharts\ 1\ to\ 4\ \(1\).jpg
```

## Information about System Architecture

This section provides information about the syntax expected by Gilbreth per the defaults defined by the authors.

### Table 1: __Syntax for Shapes__

|   Shape   	| Representation 	|
|:---------:	|:--------------:	|
|  Ellipse  	|   Start/Stop   	|
| Rectangle 	|   Instruction  	|
|  Diamond  	|    Condition   	|
|  Hexagon  	|      Loops     	|

<br>

### Table 2: __Syntax for statements__

|         Token        	|        Meaning        	|     Example     	    |
|:--------------------:	|:---------------------:	|:---------------:	    |
|          in          	|         input         	|  in: var1, var2 	    |
|          out         	|         output        	| out: var1, var2 	    |
|           =          	|  assignment operator  	|                 	    |
|   +, -, *, /, _mod_  	| arithmetic operations 	|                 	    |
|   >, <, ==, >=, <=   	|  comparison operators 	|     a _\<op>_ b    	|
|        and, or       	|    binary operators   	|                 	    |
| +=, -=, *=, /=, mod= 	|       shorthands      	|                 	    |
|        ++, --        	|    unary shorthands   	|      a _\<op>_     	|

<br>

### Table 3: __Syntax for Loops__

|  Type 	|                 Syntax                	    |         Example        	|
|:-----:	|:-------------------------------------:	    |:----------------------:	|
|  for  	| for \<init\>; \<condition\>; \<increment\>; 	| for i = 0; i < 10; i++ 	|
| while 	|           while <condition>           	    |      while i == 0      	|

<br><br>

### Grammar for Generating the Parse tree

Below is the default grammar used to generate the parse trees in our examples.  The  grammar must follow  the  standards  set by the LARK parser to be parsed completely. Note that users can set their own grammar as well and do not need to explicitly follow the below defaults.

```
expr : assign
    | io
    | for_loop
    | while_loop
    | bool
    | cond
    | "START"                   -> start
    | "STOP"                    -> stop
    | "start"                   -> start
    | "stop"                    -> stop
    | "Start"                   -> start
    | "Stop"                    -> stop
    | expr "."| [ expr ("," expr)+ ]
    
for_loop : "for" assign ";" cmp ";" assign
    | "FOR" assign ";" cmp ";" assign

while_loop : "while" cmp
    | "WHILE" cmpcond: "if" cmp 
    | "IF" cmpbool: "TRUE"                    -> true
    | "true"                    -> true
    | "True"                    -> true
    | "FALSE"                   -> false
    | "false"                   -> false
    | "False"                   -> false

cmp : arith cmpop arith | bool | [ cmp (conj cmp)+ ]

conj : "or"                     -> or
    | "and"                     -> and
    
assign : var assignop arith
    | var shortassignop arith
    | var incr_op

!?arith : arith binop arith
    | "(" arith ")"
    | SIGNED_NUMBER             -> num
    | var
    
io : iofunc ":" [ io_comp ("," io_comp)* ]

?io_comp : ESCAPED_STRING       -> str
    | var
    | SIGNED_NUMBER             -> num

cmpop : "<"                     -> lt
    | ">"                       -> gt
    | "=="                      -> eq
    | ">="                      -> ge
    | "<="                      -> le

assignop : "="

shortassignop : binop"="

binop : "+"                     -> add
    | "-"                       -> min
    | "*"                       -> mul
    | "/"                       -> div
    | "%"                       -> mod

incr_op : "++"                  -> add_incr
    | "--"                      -> min_incr
    
var : CNAMEiofunc : "in"                   -> in
    | "IN"                      -> in
    | "OUT"                     -> out
    | "out"                     -> out%import common.
    
%import common.SIGNED_NUMBER
%import common.CNAME
%import common.WS
%ignore WS
```