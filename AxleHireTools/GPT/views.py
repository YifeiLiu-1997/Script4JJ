from django.shortcuts import render
from django.http.response import HttpResponse
import openai


# Create your views here.
def gpt_index(request):
    return render(request, 'gpt_index.html')


def gen_response(request):

    user_input = request.POST['userInput']
    openai.api_key = "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"
    model_engine = "text-davinci-003"
    print(f'using {model_engine}')
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=user_input,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    response = completion.choices[0].text.replace('\n', '')
    print(response)
    return HttpResponse(response)


if __name__ == '__main__':
    gen_response()