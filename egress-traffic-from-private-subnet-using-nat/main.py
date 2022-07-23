import boto3

ec2 = boto3.resource('ec2', aws_access_key_id='AWS_ACCESS_KEY_ID',
                     aws_secret_access_key='AWS_SECRET_ACCESS_KEY',
                     region_name='us-west-2')

# create VPC and assign a name to vpc using tags
vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", "Value": "my_vpc"}])
vpc.wait_until_available()

# create and attach internet gateway
igw = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=igw.id)

# create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)

# create subnet
subnet1 = ec2.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc.id)
subnet2 = ec2.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc.id)

# create NAT gateway in public subnet, allocate an EIP to the nat gateway
ngw = ec2.create_nat_gateway(
    AllocationId='string',
    ClientToken='string',
    DryRun=True|False,
    SubnetId=subnet1.id,
    TagSpecifications=[
        {
            'ResourceType': 'natgateway',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'nat-gate-way'
                },
            ]
        },
    ],
    ConnectivityType='public'
)
# associate the route table with the subnet
route_table.associate_with_subnet(SubnetId=subnet.id)

# Create sec group
sec_group = ec2.create_security_group(
    GroupName='slice_0', Description='slice_0 sec group', VpcId=vpc.id)
sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='icmp',
    FromPort=-1,
    ToPort=-1
)
print(sec_group.id)

# find image id ami-835b4efa / us-west-2
# Create instance
instances = ec2.create_instances(
    ImageId='ami-835b4efa', InstanceType='t2.micro', MaxCount=1, MinCount=1,
    NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group.group_id]}])
instances[0].wait_until_running()
print(instances[0].id)

# create a public subnet
# create a private subnet
# create NAT gateway in public subnet, allocate an EIP to the nat gateway
# add nat-id to route table of private subnet
# 