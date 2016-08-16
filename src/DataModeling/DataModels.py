from SystemUtilities.Globals import *


# Source data data structures
class Data:
    def __init__(self, id_num):
        self.id = id_num
        self.gold_events = []
        self.predicted_events = []


class Patient(Data):
    def __init__(self, id_num):
        Data.__init__(self, id_num)
        self.doc_list = []


class Document(Data):
    def __init__(self, id_num, text):
        Data.__init__(self, id_num)
        self.highlighted_spans = {}  # {substance : [gold HighlightedSpan]}
        self.text = text
        self.sent_list = []

        self.keyword_hits = {}  # {substance_type : [KeywordHit objs]}
        self.keyword_hits_json = {}
        for substance in SUBSTANCE_TYPES:
            self.keyword_hits[substance] = []


class Sentence(Data):
    def __init__(self, id_num, text, span_in_doc_start, span_in_doc_end):
        Data.__init__(self, id_num)
        self.text = text
        self.span_in_doc_start = span_in_doc_start
        self.span_in_doc_end = span_in_doc_end
        self.tok_sent_with_crf_predicted_attribs = dict()

        self.keyword_hits = {}  # {substance_type : [KeywordHit objs]}
        for substance in SUBSTANCE_TYPES:
            self.keyword_hits[substance] = []

    def get_status_label_and_evidence(self, type):
        for evnt in self.gold_events:
            if evnt.substance_type == type:
                return_status = evnt.status
                return_text_data = self.__get_text_from_spans(evnt.status_spans, self.span_in_doc_start, self.span_in_doc_end)
                return return_status, return_text_data
        return "unknown", "evidence unavailable"

    def __get_text_from_spans(self, span_list, sent_begin, sent_end):
        spans = list()
        for span in span_list:
            true_start = span.start - sent_begin
            true_end = span.stop - sent_begin
            if true_start > -1 and true_start < len(self.text) and true_end <= len(self.text):
                spans.append((self.text[true_start:true_end], Span(true_start, true_end)))
        return spans


class Field:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.spans = []


class HighlightedSpan:
    def __init__(self, field, value, span_start, span_end):
        self.field = field
        self.value = value
        self.span = Span(span_start, span_end)


class Span:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop


# Substance information templates
class Event:
    def __init__(self, substance):
        self.substance_type = substance
        self.status = ""
        self.attributes = {}    # {attrib_name: Attribute object}


class DocumentEvent(Event):
    def __init__(self, substance):
        Event.__init__(self, substance)
        self.status_spans = []  # list of Span objects -- all values found for this field


class PatientEvent(Event):
    def __init__(self, substance):
        Event.__init__(self, substance)
        self.status_spans = {}  # {doc_id: [Span]} -- all values found for this field for each doc


class Attribute:
    def __init__(self, attribute_type, span_start, span_end, text):
        self.type = attribute_type
        self.span_start = span_start
        self.span_end = span_end
        self.text = text


class AnnotatedAttribute:
    def __init__(self, attribute_type, spans, text):
        self.type = attribute_type
        self.spans = spans
        self.text = text


class DocumentAttribute(Attribute):
    def __init__(self, attribute_type, span_start, span_end, text, all_values_for_field):
        Attribute.__init__(self, attribute_type, span_start, span_end, text)
        self.all_value_spans = []   # list of Span objects -- all values found for this field

        # find all values' spans
        spans = [Span(attrib.span_start, attrib.span_end) for attrib in all_values_for_field]
        self.all_value_spans = spans


class PatientAttribute(Attribute):
    def __init__(self, attribute_type, span_start, span_end, text, doc_id, all_values_for_field, all_doc_ids):
        Attribute.__init__(self, attribute_type, span_start, span_end, text)

        self.document = doc_id
        self.all_doc_value_spans = {}   # {doc_id: [Span]} -- all values found for this field for each doc

        # find all spans for the attribute for all docs
        for attrib, doc_id in zip(all_values_for_field, all_doc_ids):
            self.all_doc_value_spans[doc_id] = attrib.all_value_spans
