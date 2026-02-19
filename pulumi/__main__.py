"""Pulumi program for Yandex.Cloud using pulumi_yandex 0.13.0"""

import pulumi
import pulumi_yandex as yandex

config = pulumi.Config("yandex")
zone = config.require("zone")
my_ip = "151.243.28.100/32"

# ===== Network =====
network = yandex.VpcNetwork("devops-network")

subnet = yandex.VpcSubnet(
    "devops-subnet",
    zone=zone,
    network_id=network.id,
    v4_cidr_blocks=["10.0.1.0/24"]
)

# ===== Security Group с ingresses/egresses =====
sg = yandex.VpcSecurityGroup(
    "devops-sg",
    network_id=network.id,
    ingresses=[
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            from_port=22,
            to_port=22,
            v4_cidr_blocks=[my_ip],
            description="SSH"
        ),
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            from_port=80,
            to_port=80,
            v4_cidr_blocks=["0.0.0.0/0"],
            description="HTTP"
        ),
        yandex.VpcSecurityGroupIngressArgs(
            protocol="TCP",
            from_port=5000,
            to_port=5000,
            v4_cidr_blocks=["0.0.0.0/0"],
            description="App port 5000"
        ),
    ],
    egresses=[
        yandex.VpcSecurityGroupEgressArgs(
            protocol="ANY",
            v4_cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound"
        )
    ]
)

# ===== VM =====
image = yandex.get_compute_image(family="ubuntu-2204-lts")

vm = yandex.ComputeInstance(
    "devops-vm",
    platform_id="standard-v2",
    resources=yandex.ComputeInstanceResourcesArgs(
        cores=2,
        memory=1,
        core_fraction=20
    ),
    boot_disk=yandex.ComputeInstanceBootDiskArgs(
        initialize_params=yandex.ComputeInstanceBootDiskInitializeParamsArgs(
            image_id=image.id,
            size=10,
            type="network-hdd"
        )
    ),
    network_interfaces=[
        yandex.ComputeInstanceNetworkInterfaceArgs(
            subnet_id=subnet.id,
            nat=True,
            security_group_ids=[sg.id]
        )
    ],
    metadata={
        "ssh-keys": "ubuntu:" + open("/home/dreamcore/.ssh/devops_vm_key.pub").read().strip()
    }
)

pulumi.export("public_ip", vm.network_interfaces[0].nat_ip_address)
