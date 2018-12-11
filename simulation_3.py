from network_3 import Router, Host
from link_3 import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 30  # give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads at the end

    # create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)

    # create routers and routing tables for connected clients (subnets)
    #Label frame based on the dst, Assigns 11 to ip packets
    encap_tbl_D = {'H3' : '11'}  # table used to encapsulate network packets into MPLS frames
    # table used to forward MPLS frames, {in_label{in_intf:(outlabel, out_inft}}
    frwd_tbl_D = {'11':
                    {
                        #From H1 out interface 2 to router B
                        0:('22',2),
                        #From H2 out interface 3 to router C
                        1: ('22',3)}
                    }
    decap_tbl_D = {'22': (True, 0)}  # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA',
                      intf_capacity_L=[500, 500, 500,500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_a)

    encap_tbl_D = {}
    #Just need to forward packets on direction, from 0 intf to 1 intf
    frwd_tbl_D = {'22':
                      {0:('22',1)}
                  }
    decap_tbl_D = {}
    router_b = Router(name='RB',
                      intf_capacity_L=[500, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_b)

    encap_tbl_D = {}
    # Just need to forward packets on direction, from 0 intf to 1 intf
    frwd_tbl_D = {'22':
                      {0:('22',1)}
                  }
    decap_tbl_D = {}
    router_c = Router(name='RC',
                      intf_capacity_L=[500,500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_c)

    encap_tbl_D = {}
    frwd_tbl_D = {'33': {0:('22',1)}}
    decap_tbl_D = {'22' : (True, 2)}
    router_d = Router(name='RD',
                      intf_capacity_L=[500, 100, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_d)

    # create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)

    #A Links
    link_layer.add_link(Link(host_1, 0, router_a, 0))

    link_layer.add_link(Link(host_2, 0, router_a, 1))

    link_layer.add_link(Link(router_a, 2, router_b, 0))
    link_layer.add_link(Link(router_a, 3, router_c, 0))

    #B links
    link_layer.add_link(Link(router_b, 1, router_d, 0))

    #C Links
    link_layer.add_link(Link(router_c, 1, router_d, 1))

    #D links
    link_layer.add_link(Link(router_d, 2, host_3, 0))

    # start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run))

    for t in thread_L:
        t.start()

    # create some send events
    for i in range(1):
        priority = i % 2
        host_1.udt_send('H3', 'FIRST_MESSAGE_%d_FROM_H1_With_Priority_0' % i, 0)
        host_2.udt_send('H3', 'FIRST_MESSAGE_%d_FROM_H2_With_Priority_0' % i, 0)
        host_1.udt_send('H3', 'SECOND_MESSAGE_%d_FROM_H1_With_Priority_1' % i, 0)
        host_2.udt_send('H3', 'SECOND_MESSAGE_%d_FROM_H2_With_Priority_1' % i, 0)
        host_1.udt_send('H3', 'THIRD_MESSAGE_%d_FROM_H1_With_Priority_0' % i, 0)
        host_2.udt_send('H3', 'THIRD_MESSAGE_%d_FROM_H2_With_Priority_1' % i, 0)
        host_1.udt_send('H3', 'FOURTH_MESSAGE_%d_FROM_H1_With_Priority_1' % i, 0)
        host_2.udt_send('H3', 'FOURTH_MESSAGE_%d_FROM_H2_With_Priority_0' % i, 0)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")
