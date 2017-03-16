#! /usr/bin/env python2

import boto.ec2

regions = ['us-east-1']
#region_list = [x.name for x in conn.get_all_regions()]

def main():
    for region in regions:
        conn = boto.ec2.connect_to_region(region)
        instances = conn.get_only_instances(
            filters={"tag:InstanceHibernate":"*"})
        for inst in instances:
            hibernationTag = inst.tags.get('InstanceHibernate', "NONE!")
            print "{:22} Tag:{:10} {}".format(inst.id, hibernationTag, inst.state)

if __name__ == '__main__':
    main()
