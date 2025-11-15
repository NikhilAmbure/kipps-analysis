import re
import random
from datetime import datetime
from nltk.corpus import wordnet as wn
from textblob import TextBlob


def analyze_conversations(conversation):
    
    messages = conversation.messages.all().order_by('timestamp')
    
    user_msgs = [m.text for m in messages if m.sender == 'user']
    ai_msgs = [m.text for m in messages if m.sender == 'ai']
    
    clarity = clarity_score(ai_msgs)
    relevance = relevance_score(messages)
    accuracy = accuracy_score(ai_msgs)
    completeness = completeness_score(messages)
    sentiment = sentiment_analysis(user_msgs)
    empathy = empathy_score(ai_msgs)
    fallback_count_val = fallback_count(ai_msgs)
    escalation_needed_val = fallback_count_val > 0
    avg_response_time = average_response_time(messages)
    resolution = detect_resolution(user_msgs)
    
    overall = (clarity + relevance + accuracy + completeness + empathy) / 5
    
    return {
        "clarity_score": clarity,
        "relevance_score": relevance,
        "accuracy_score": accuracy,
        "completeness_score": completeness,
        "sentiment": sentiment,
        "empathy_score": empathy,
        "fallback_count": fallback_count_val,
        "escalation_needed": escalation_needed_val,
        "average_response_time": avg_response_time,
        "resolution": resolution,
        "overall_score": overall,
    }
    

# clarity_score
def clarity_score(ai_messages):
    if not ai_messages:
        return 0
    
    clear_resp = 0
    for msg in ai_messages:
        words = msg.split()
        
        if len(words) <= 25 and len(words) >= 3:
            clear_resp += 1

    return clear_resp / len(ai_messages)



# Relevance_score(WordNet)
def get_synonyms(word):
    synonyms = set()
    
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace("_", " "))
    return synonyms

def are_semantically_same(word1, word2):
    syn1 = get_synonyms(word1)
    syn2 = get_synonyms(word2)
    return not syn1.isdisjoint(syn2) # at least 1 common synonym
    

def relevance_score(messages):
    relevance_sum = 0
    pairs = 0
    
    for i in range(len(messages) - 1):
        
        if messages[i].sender == "user" and messages[i + 1].sender == "ai":
            user_words = messages[i].text.lower().split()
            ai_words = messages[i+1].text.lower().split()
            
            score = 0
            for i1 in user_words:
                for i2 in ai_words:
                    if i1 == i2 or are_semantically_same(i1, i2):
                        score+=1
                        
            total_possible = len(user_words)
            relevance_sum += (score / (total_possible + 1))
            pairs += 1
            
    return relevance_sum / pairs if pairs else 1
    
    
# Accuracy score :
"""
     Note: Accuracy is measured as a confidence score based on the presence
     of uncertain language. While not perfect, this serves as a reasonable
     proxy for factual accuracy in the absence of a knowledge base for
     actual fact-checking.
"""
def accuracy_score(ai_messages):
    uncertain_phrases = [
        "maybe", "not sure", "i think", "possibly", "perhaps",
        "i believe", "i'm not sure", "it might be", "it could be",
        "probably", "i'm guessing", "unsure", "unclear"
    ]
    
    if not ai_messages:
        return 0.5
    
    score = 0
    for msg in ai_messages:
        if any(word in msg.lower() for word in uncertain_phrases):
            score += 0.5
        else:
            score += 1
        
    return score / len(ai_messages)



# completeness_score 
def completeness_score(messages):
    for i in range(len(messages) - 1):
        if messages[i].sender == "user":
            if messages[i+1].sender == "user":
                return 0.5
            
    return 1


# sentiment_score (TextBlob): 
"""
    Handles emotional language automatically
"""
def sentiment_analysis(user_messages):
    if not user_messages:
        return "neutral"
    
    total = [TextBlob(msg).sentiment.polarity for msg in user_messages]
    avg_polarity = sum(total) / len(user_messages) if total else 0
    
    if avg_polarity > 0.2:
        return "positive"
    elif avg_polarity < -0.2:
        return "negative"
    else:
        return "neutral"
    
    
# Empathy score
def empathy_score(ai_messages):
    empathy_phrases = [
        "sorry", "apologize", "my apologies", "regret",
        "understand", "i see", "i hear", "that makes sense",
        "i can imagine", "that sounds",
        "don't worry", "no problem", "it's okay", "not to worry",
        "i'm here to help", "let me help", "how can i assist",
        "we'll figure this out", "we can work on this",
        "frustrating", "annoying", "disappointing", "challenging",
        "thank you for sharing", "appreciate you telling me"
    ]
    
    if not ai_messages:
        return 0
    
    score = 0
    for msg in ai_messages:
        if any(w in msg.lower() for w in empathy_phrases):
            score += 1
            
    return score / len(ai_messages) 



# Fallback frequency
def fallback_count(ai_messages):
    fallback_phrases = [
        "i don't know", "i don't understand", "not sure", "unsure",
        "i cannot help", "i can't help", "unable to help", "cannot assist",
        "let me transfer", "let me connect you", "contact a human",
        "speak to an agent", "outside my knowledge", "beyond my capabilities"
    ]
    
    count = 0
    for msg in ai_messages:
        if any(w in msg.lower() for w in fallback_phrases):
            count += 1
    
    return count


# resolution score
def detect_resolution(user_messages):
    
    if not user_messages:
        return False
    
    resolution_phrases = [
        "thanks", "thank you", "great", "perfect", "awesome",
        "got it", "that works", "problem solved", "it works",
        "resolved", "fixed", "working now", "all set", "done",
        "that helped", "you helped", "appreciate it"
    ]
    
    negative_phrases = [
        "thanks for nothing", "still not", "doesn't work",
        "no help", "useless", "waste of time", "never mind"
    ]
    
    last = [user_messages[-1]]
    if len(last) > 1:
        last.append(user_messages[-2])
        
    for msg in user_messages:
        if any(w in msg.lower() for w in resolution_phrases):
            """ if last message is not negative or sarcastic """
            if not any(neg in msg.lower() for neg in negative_phrases):
                return True
    
    return False


# Average response time
def average_response_time(messages):
    times = []
    
    for i in range(len(messages) - 1):
        if messages[i].sender == "user" and messages[i+1].sender == "ai":
            t1 = messages[i].timestamp
            t2 = messages[i+1].timestamp
            diff = (t2 - t1).total_seconds()
            times.append(diff)
    
    return sum(times) / len(times) if times else None