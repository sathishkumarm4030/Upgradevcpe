def get_vd_details():
    ip = raw_input("Enter Versa Director IP address:\n")
    print "Versa director IP:" + ip
    user = raw_input("Enter Versa Director Username:\n")
    print "Versa director IP:" + user
    passwd = raw_input("Enter Versa Director Password:\n")
    day = raw_input("Enter DAY:\n")
    print "DAY:" + day
    # ip = '10.91.127.194'
    # user = 'MSK'
    # passwd = 'Versa@123'
    # day = '2'
    return {'ip' : ip, 'user': user, 'passwd': passwd, 'day' : day}



#Variables
task_url = "/api/operational/tasks/task/"
upgrade_dev_url = "/api/config/nms/actions/packages/upgrade"
headers = {'Accept': 'application/vnd.yang.data+json'}
headers2 = {'Accept': 'application/vnd.yang.data+json', 'Content-Type': 'application/vnd.yang.data+json'}
headers3 = {'Accept': 'application/json', 'Content-Type': 'application/json'}

vd_dict = get_vd_details()
vdurl = 'https://' + vd_dict['ip'] + ':9182'
user = vd_dict['user']
passwd = vd_dict['passwd']
day = vd_dict['day']
vd_ssh_dict = {
    'device_type': 'versa',
    'ip': vd_dict['ip'],
    'username': 'admin',
    'password': 'versa123',
    'port': 22,
}

cmd1 = 'show interfaces brief | tab | nomore'
cmd2 = 'show bgp neighbor brief | nomore'
cmd3 = 'show route | nomore'
cmd4 = 'show configuration | display set | nomore'

