from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.shortcuts import get_object_or_404, render

from django.views import generic
from .models import Choice, Question




# generic views

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


# custom views, creates redundancy

# def index(request):
#     # return HttpResponse("Hello, world. You're at the polls index.")

#     # hardcoded list
#     # latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     # output = ", ".join([q.question_text for q in latest_question_list])
#     # return HttpResponse(output)


#     # dynamic list
#     # latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     # template = loader.get_template("polls/index.html")
#     # context = {
#     #     "latest_question_list": latest_question_list,
#     # }
#     # return HttpResponse(template.render(context, request))

#     # render is a shortcut, we give it the request, the template path,
#     # and context, no need to import loader and HttpResponse
#     latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     context = {"latest_question_list": latest_question_list}
#     return render(request, "polls/index.html", context)

 
# def detail(request, question_id):
#     # return HttpResponse("You're looking at question %s." % question_id)

#     question = get_object_or_404(Question, pk=question_id) 
#     return render(request, "polls/detail.html", {"question": question})



# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)   
#     return render(request, "polls/results.html", {"question": question})


def plot_results(request, question_id):

    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from PIL import Image
    import io

    question = get_object_or_404(Question, pk=question_id) 

    # Fetch data from the database

    choices = []
    votes = []
    for choice in question.choice_set.all():
        choices.append(choice.choice_text)
    for choice in question.choice_set.all():
        votes.append(choice.votes)

    print(votes)

    # Generate the plot
    fig = plt.figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1, 1, 1)
    ax.bar([x for x in range(len(choices))], votes)
    ax.set_xlabel('Choices')
    ax.set_ylabel('Votes')
    ax.set_title('Voting Results')
    ax.set_xticks([x for x in range(len(choices))])
    ax.set_xticklabels(choices, fontsize=18)
    canvas.draw()

    # Convert the plot to PNG format
    buf = io.BytesIO()
    canvas.print_png(buf)
    plt.close(fig)

    # Retrieve the PNG image data from the buffer
    image_data = buf.getvalue()
    buf.close()

    # Return the image data as an HTTP response with the appropriate content type
    response = HttpResponse(content_type='image/png')
    response.write(image_data)
    return response




def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))