import redis

r = redis.Redis(host='192.168.86.202', port=6379, db=0)
setter = r.set('foo', 'bar')
getter = r.get('foo')

if setter == True and getter == b'bar':
    print("Redis is running correctly")