We can pass a variable number of arguments to a function using special symbols:

* `*args` (Non-Keyword Arguments)
* `**kwargs` (Keyword Arguments)

> We use the “wildcard” or “*” notation like this – `*args` OR `**kwargs` – as our function’s argument when we have doubts about the number of arguments we should pass in a function.

con non-keyworded se hace refencia a argumentos pasados de esta manera: `my_func("hello", "world")`.

con keyworded se hace refencia a argumentos pasados de esta manera: `my_func(first="hello", second="world")`.

> Siempre que se usa una funcion en Python deben ir primero los non-keyworded y despues los keyworded.

# `*args`

this special sintax in function definitions is used to pass a non-keyworded, variable-length argument list. 

* by convention, it is often used with the word **args**
* any number of extra arguments can be tacked on to your current formal parameters (including zero extra arguments).

es decir, cuando estoy definiendo una función puedo acceder a una lista de argumentos de longitud desconida.


# `**kwargs`

this special sintax in function definitions is used to pass a keyworded, variable-length argument list.

````py
def myFun(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} is {value}")

myFun(first='Geeks', mid='for', last='Geeks')
````


# Using *args and **kwargs

* `*args` receives arguments as a **tuple**.
* `**kwargs` receives arguments as a **dictionary**.

puedo llamar funciones así 

```py
args = ("Geeks", "for", "Geeks")
myFun(*args)
 
kwargs = {"arg1": "Geeks", "arg2": "for", "arg3": "Geeks"}
myFun(**kwargs)
```

y si quiero usar `*args` y `**kwargs` en una misma función la defino así:  `def myFun(*args, **kwargs):`. Esto implica que acceso a los valores de así: `args[0]` y `kwargs["key"]`

