from time import sleep
import boto3

# Using default config profile
client = boto3.client('ec2')

# create VPC and assign a name to vpc using tags

vpc = client.create_vpc(CidrBlock='192.168.0.0/16')
client.create_tags(Resources=[vpc['Vpc']['VpcId']],
                   Tags=[{"Key": "Name", 
                       "Value": "my_vpc"
                       }]
                )

# create and attach internet gateway to the vpc 
igw = client.create_internet_gateway()
client.attach_internet_gateway(InternetGatewayId=igw['InternetGateway']['InternetGatewayId'],
                               VpcId=vpc['Vpc']['VpcId']) 

# create subnet
public_subnet_1 = client.create_subnet(CidrBlock='192.168.0.0/24', VpcId=vpc['Vpc']['VpcId'])
private_subnet_1 = client.create_subnet(CidrBlock='192.168.128.0/24', VpcId=vpc['Vpc']['VpcId'])

# create an Elastic IP address
# Note if this elastic ip is not used it will incur charges
eip = client.allocate_address(Domain='vpc',
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
    AllocationId=eip['AllocationId'],
    SubnetId=public_subnet_1['Subnet']['SubnetId'],
    TagSpecifications=[{
        'ResourceType': 'natgateway',
        'Tags': [{
            'Key': 'Name',
            'Value': 'nat-gate-way'
            }]
        }]
    )

print('waiting for nat gateway creation')
sleep(180) # waiting for nat gateway to be available
print(f"state of nat gateway is : {ngw['NatGateway']['State']}")


# create a route table and a public route
vpc_route_table = client.create_route_table(VpcId=vpc['Vpc']['VpcId'])
route = client.create_route(DestinationCidrBlock='0.0.0.0/0',
                            GatewayId=igw['InternetGateway']['InternetGatewayId'],
                            RouteTableId=vpc_route_table['RouteTable']['RouteTableId'])

private_route_table = client.create_route_table(VpcId=vpc['Vpc']['VpcId'])
route = client.create_route(DestinationCidrBlock='0.0.0.0/0',
                            NatGatewayId=ngw['NatGateway']['NatGatewayId'],
                            RouteTableId=private_route_table['RouteTable']['RouteTableId'])

# associate the route table with the subnet
client.associate_route_table(RouteTableId=vpc_route_table['RouteTable']['RouteTableId'],
                             SubnetId=public_subnet_1['Subnet']['SubnetId'])
client.associate_route_table(RouteTableId=private_route_table['RouteTable']['RouteTableId'],
                             SubnetId=private_subnet_1['Subnet']['SubnetId'])

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
            }]
    )

# creating the key pair
key_pair = client.create_key_pair(
    KeyName='my-key-pair',
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
    )
print('now waiting for ec2 instance')
sleep(180) # waiting for nat gateway to be available

ec2_info = ['ImageId', 'InstanceId','InstanceType', 'KeyName',
            'LaunchTime','Monitoring', 'Platform',
            'State', 'SubnetId','VpcId','Architecture']

for _property in ec2_info:
    print(f"{_property}\t {ec2_instance['Instances'][0][_property]}\n")