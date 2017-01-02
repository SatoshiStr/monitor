import ceilometerclient.client

auth_args = {
    'auth_url': 'http://10.10.1.11:35357/v3',
    'project_name': 'admin',
    'user_domain_name': 'default',
    'project_domain_name': 'default',
    'username': 'admin',
    'password': 'admin123',
}
cclient = ceilometerclient.client.get_client(2,
    os_username=auth_args['username'], os_password=auth_args['password'],
    os_tenant_name=auth_args['project_name'],
    os_user_domain_name=auth_args['user_domain_name'],
    os_project_domain_name=auth_args['project_domain_name'],
    os_auth_url=auth_args['auth_url'])

query = [
    dict(field='resource_id', op='eq',
         value='f0bb0224-dab6-4531-bf63-94fe2d5b7686'),
    dict(field='meter',op='eq',value='cpu_util')
]
for sample in cclient.new_samples.list(q=query, limit=1):
    print 'util %s|cpu_util=%s;;;;' % (sample.volume, sample.volume)
