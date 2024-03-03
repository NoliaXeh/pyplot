# PyPlot

PyPlot is a tool for generating anything based on a sequence diagram, named Plot bu this library.

## Usage

Start by creating a .plot file describing your scenario
```plot
# sequence.plot
Client      Server
|              |
|------------->| HTTP GET { "path": "/rest/names", "content": "" }
|<-------------| HTTP 200 { "content": [ "john", "bob", "alice" ] }
```

Then, create your templates for heach messages type:
```py
{# templates/HTTP_GET.templ #}
GET {{message.sender.data.url}}{{message.data.path}} HTTP/1.1
Content-Lenth: {{message.data.content|length}}

{{message.data.content}}
```

```py
{# templates/HTTP_200.templ#}
HTTP/1.1 200 OK
Content-Lenth: {{message.data.content|length}}

{{message.data.content}}
```

Then, start coding.
Beggin by parsing your Plot file
```py
import pyplot

plot = pyplot.Plot("Scenario 1", "scenarios/sequence.plot")
try:
    plot.parse()
except pyplot.PlotError as e:
    print("Error parsing file. Exiting. ")
    print (e)
    exit(1)
```
Then, play your plot with `pyplot.play(plot)`

```py
...
result: str = pyplot.play(plot)
```

If you run this, you should see nothing else that parse errors if any. You nee to add actions to do anything
For this exemple, we will make two actions. One to print the parsed messages, one to fill templates

An action is a class, decoratoed with eighter `pyplot.action` or `pyplot.template_action`
A class decorated with `pyplot.action` must provide a `trigger` and an `execute` static method.
- `trigger` takes two args, `plot: pyplot.Plot` and `message: pyplot.Message`.
   It returns a boolean. If the boolean is `True`, then the `execute` method will be called
- `execute` takes the same two args, `plot: pyplot.Plot` and `message: pyplot.Message` and returns either a string or None
   This is called on `pyplot.play` if `trigger` returns `True`. It it returns a string, it is appened to the return value of `pyplot.play`

Example:
The followoing action is triggered on any message, and when executed, prints informations about the message in stdout
```py
@pyplot.action
class PrintAction:
    @staticmethod
    def trigger(plot: pyplot.Plot, message: pyplot.Message) -> bool:
        return True

    @staticmethod
    def execute(plot: pyplot.Plot, message: pyplot.Message):
        print(f"""\
Message #{message.order + 1}: {message.title!r}
  | From: {message.sender}
  | To: {message.receiver}
  | Content: {message.content}
  | Data: {message.data}\
""")
```

The library provides some helper decorators, enabling to reuse methodes for triggers or for execution.
Example, rewriting the same action with decorators:

```py
def print_message(plot, message: pyplot.Message):
        print(f"""\
Message #{message.order + 1}: {message.title!r}
  | From: {message.sender}
  | To: {message.receiver}
  | Content: {message.content}
  | Data: {message.data}\
""")
def always(plot, message: pyplot.Message) -> bool:
    return True

@pyplot.action
@pyplot.trigger(always)
@pyplot.execute(print_message)
class PrintAction:
    pass
```

If you provide both decorator and static method, the static method is prefered and the decorator is ignored.

Now let's get into real business with `pyplot.template_action`
When you decorate with this, it is like decorating with `pyplot.action`. By the `trigger` and `execute` methods will be generated if you do not provide them, using some params you provide as class properties.

Let's see an example:
```py
@pyplot.template_action
class HttpGetAction:
    message = 'HTTP GET'
    template = 'templates/HTTP_GET.templ'
```
Yes, it is that concise.
Now when decorating this class, `pyplot.template_action` will look for the `message` property, and generate the `trigger` method to test if the message is `HTTP GET`. Like `pyplot.action`, this behaviour is overidden if you provide manually a `trigger` method.
The, `pyplot.template_action` will look for the `template` property, and will generate the `execute` method to render the template you just named with the message informations.

Now let's add an action for the response:
```py
@pyplot.template_action
class HttpGetAction:
    message = 'HTTP 200'
    template = 'templates/HTTP_200.templ'
```
And done. Now, the code looks like this:

```py
import pyplot


@pyplot.template_action
class HttpGetAction:
    message = 'HTTP GET'
    template = 'templates/HTTP_GET.templ'

@pyplot.template_action
class HttpGetAction:
    message = 'HTTP 200'
    template = 'templates/HTTP_200.templ'

plot = pyplot.Plot("Scenario 1", "scenarios/sequence.plot")
try:
    plot.parse()
except pyplot.PlotError as e:
    print("Error parsing file. Exiting. ")
    print (e)
    exit(1)

result = pyplot.play(result)
print(result)

```

If you run it, you will get
```
GET /rest/names HTTP/1.1
Content-Lenth: 0

HTTP/1.1 200 OK
Content-Lenth: 26

[ "john", "bob", "alice" ]
```

Everything is nice, except that the `{{message.sender.data.url}}` wasn't filled. That is because we did not provide any data for the `Client` actor. You must provide it after parsing and befor executing, via the `Plot.set_actor_data`.

Like this:

```py
import pyplot


@pyplot.template_action
class HttpGetAction:
    message = 'HTTP GET'
    template = 'templates/HTTP_GET.templ'

@pyplot.template_action
class HttpGetAction:
    message = 'HTTP 200'
    template = 'templates/HTTP_200.templ'

plot = pyplot.Plot("Scenario 1", "scenarios/sequence.plot")
plot.set_actor_data("Client", {"url": "/server"})

try:
    plot.parse()
except pyplot.PlotError as e:
    print("Error parsing file. Exiting. ")
    print (e)
    exit(1)

result = pyplot.play(result)
print(result)
```

Now tou should get:
```
GET /server/rest/names HTTP/1.1
Content-Lenth: 0

HTTP/1.1 200 OK
Content-Lenth: 26

[ "john", "bob", "alice" ]
```