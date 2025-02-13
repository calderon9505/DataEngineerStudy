from datetime import datetime

def execution_time(func):
    def wrapper(*args, **kwargs):
        initial_time = datetime.now()
        func(*args, **kwargs)
        final_time = datetime.now()
        time_elapsed = final_time - initial_time
        print(f'Pasaron {time_elapsed.total_seconds()} segundos')
    return wrapper

@execution_time
def random_func():
    for _ in range(1, 10_000_000):
        pass

@execution_time
def suma(a,b):
    return a+b

random_func()
suma(3,5)

# eliminando repetidos
lista = [1,1,2,2,4]
print(list(set(lista)))