## Transient Cluster on AWS from Scratch using boto3 | Trigger Spark job from AWS Lambda

### Step 1: Code bucket Creation (codefilelocation) . Inside this bucket upload the spark.py file .

### Step 2: Source Bucket Creation (landings3buckettransient)

### Step 3: Destination bucket creation (destinationbucketprocessed)

### Step 4: IAM Role for Lambda

- Go to IAM -> Roles -> create a role -> use case : Lambda , attacth S3FullAccess , CloudWatchFullAccess , AmazonEMRFullAccessPolicy

### Step 5: Lambda Function with s3 trigger creation

- Go to aws -> Lambda -> create function -> Runtime: python 3.9 | Execution role : Use an existing role , and select the role we created , now create the function
- Now click on trigger -> and select S3 -> Bucket : landings3transient -> click on add
- Now click on our lambda -> Code -> Copy the code in lambda.py and paste it over there
- Now click on deploy
- Now whenever a file lands in our landings3buckettransient bucket lambda will be triggered
