from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("audio/", views.audio, name="audio"),
    path("satzgenerator/", views.satzgenerator, name="satzgenerator"),
    path("recursiveresponse/", views.recursiveresponse, name="recursiveresponse"),
    path("get_other_transcripts/", views.get_other_transcripts, name="other_transcripts"),
    path("buchstaben_scores/", views.buchstaben_scores, name="buchstaben_scores"),
    path("privacy-policy/", views.privacypolicy, name="privacy_policy"),
    path("sources/", views.sources, name="sources"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("kontakt/", views.kontakt, name="kontakt"),
    path("training/", views.training, name="training"),
    path("terms/", views.terms, name="terms"),
    
    path("robots.txt", views.robots_txt),

    
]




