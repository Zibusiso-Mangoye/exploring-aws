# Egress traffic from a private subnet using a NAT gateway

Egress traffic as explained by [technopedia](https://www.techopedia.com/definition/2398/egress-traffic) is a term used to define the volume and substance of traffic transmitted from the host network to an external network destination.

## Architecture
![img](./img/ACCESSING%20THE%20INTERNET%20FROM%20AN%20EC2%20INSTANCE%20INSIDE%20A%20PRIVATE%20SUBNET%20USING%20A%20NAT%20GATEWAY%20(1).png)

The code in this repo creates an environment like the one above. 

## Running the code

<span style="color:red">Note: NAT gateways involve using an elastic IP which is chargeable if not used therefore runnning this project may result in a bill. Therefore I will not be responsible for the charges accumulated by running this repo.</span>

### Prerequisites
1. **Setup AWS credentials** - 
Run this command to quickly set and view your credentials, Region, and output format. 
    ```
        aws configure
    ```
    *The following example shows sample values.*
    ```
        AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
        AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        Default region name [None]: us-west-2
        Default output format [None]: json
    ```
    For more information on how to set your AWS credentials click [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
    
1. **AWS SDK** [Boto3](https://docs.aws.amazon.com/pythonsdk/?id=docs_gateway)
The AWS SDK for Python (Boto3) provides a Python API for AWS infrastructure services. Using the SDK for Python, you can build applications on top of Amazon S3, Amazon EC2, Amazon DynamoDB, and more.

    ```
        pip install boto3 
    ```

Run the following command in your terminal.
```
    python main.py
```
This will create and provision AWS services as depicted in the architecture diagram above.