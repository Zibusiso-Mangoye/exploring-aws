import boto3

# Using default config profile
client = boto3.client('ec2')

# create VPC and assign a name to vpc using tags
vpc = client.create_vpc(CidrBlock='192.168.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", 
                       "Value": "my_vpc"
                       }]
                )
vpc.wait_until_available()

# create and attach internet gateway to the vpc
igw = client.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=igw['InternetGateway']['InternetGatewayId']) 

# create subnet
public_subnet_1 = client.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc['Vpc']['VpcId'])
private_subnet_1 = client.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc['Vpc']['VpcId'])

# create an Elastic IP address
# Note if this elastic ip is not used it will incur charges
eip = client.allocate_address(Domain='vpc',
                              DryRun=True,
                              TagSpecifications=[{
                                  'ResourceType': 'elastic-ip',
                                  'Tags': [{
                                      'Key': 'Name',
                                      'Value': 'my-eip-1'
                                      }]
                                  }]
                              )

# create NAT gateway in public subnet, allocate an EIP to the nat gateway
ngw = client.create_nat_gateway(
    AllocationId=eip['PublicIp'],
    DryRun=True,
    SubnetId=public_subnet_1['Subnet']['SubnetId'],
    TagSpecifications=[{
        'ResourceType': 'natgateway',
        'Tags': [{
            'Key': 'Name',
            'Value': 'nat-gate-way'
            }]
        }]
    )

# create a route table and a public route
vpc_route_table = client.create_route_table(DryRun=True, VpcId=vpc.id)
route = vpc_route_table.create_route(DestinationCidrBlock='0.0.0.0/0',
                                     GatewayId=igw['InternetGateway']['InternetGatewayId'])

private_route_table = client.create_route_table(DryRun=True, VpcId=vpc.id)
route = private_route_table.create_route(DestinationCidrBlock='0.0.0.0/0',
                                         NatGatewayId=ngw['NatGateway']['NatGatewayId'])

# associate the route table with the subnet
vpc_route_table.associate_with_subnet(SubnetId=public_subnet_1['Subnet']['SubnetId'])
private_route_table.associate_with_subnet(SubnetId=private_subnet_1['Subnet']['SubnetId'])

# Creating a security group
sec_group = client.create_security_group(
    Description='This security group allows outbound traffic to all ports, all protocols to any destination address',
    GroupName='web-access',
    VpcId=vpc['Vpc']['VpcId'],
    TagSpecifications=[{
            'ResourceType':'security-group',
            'Tags': [{
                    'Key': 'Name',
                    'Value': 'web-access'
                }]
            }],
    DryRun=True
    )

# creating the key pair
key_pair = client.create_key_pair(
    KeyName='my-key-pair',
    DryRun=True,
    KeyType='rsa',
    TagSpecifications=[
        {
            'ResourceType': 'key-pair',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'my-key-pair-ec2'
                },
            ]
        },
    ],
    KeyFormat='pem'
)

# Create instance
# Amazon Linux 2 AMI (HVM) - Kernel 5.10, SSD Volume Type
# ami-0cff7528ff583bf9a (64-bit (x86)) - us-east-1
ec2_instance = client.run_instances(
    ImageId='ami-0cff7528ff583bf9a',
    InstanceType='t2.micro', 
    MaxCount=1, 
    MinCount=1,
    KeyName='my-key-pair',
    SecurityGroupIds=[sec_group['GroupId']],
    SubnetId=private_subnet_1['Subnet']['SubnetId'],
    DryRun=True
    )
ec2_instance[0].wait_until_running()

ec2_info = ['OwnerId', 'RequesterId', 'ImageId',
            'InstanceId','InstanceType', 'KeyName',
            'LaunchTime','Monitoring', 'Platform',
            'State', 'SubnetId','VpcId','Architecture']

for _property in ec2_info:
    print(f"{_property}\t {ec2_instance[_property]}\n")