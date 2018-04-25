import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tag.stanford import StanfordNERTagger
from scipy.sparse import hstack
from sklearn.svm import LinearSVC
from practnlptools.tools import Annotator
from readproperties import read_property
import naiveBayes
import pickle
#
# ##removing special characters from sentence##
annotator = Annotator()
st = StanfordNERTagger(read_property('StanfordNerClassifier'), read_property('StanfordNerJarPath'))
f = open(read_property('testfilepath'), "r")
fi = open(read_property('FineOutputfilesPath') + 'fine_classification.txt', "w")	
t_class = []
row = 0
for line in f:
	label = (line.split()[0]).split(":")[0]
	file_w = read_property('FineInputFiles') + label + "_training.txt"
	fa = open(file_w, "r")
	train_class = []
	for each_line in fa:
		# print each_line
		l = each_line.split()[1].split(":")[1]
		# print l
		train_class.append(l)
	# print train_class
	fa.close()
	# print "The label is",label
	file_word = read_property('FineOutputfilesPath') + label + "_training_word.txt" 
	file_POS = read_property('FineOutputfilesPath') + label + "_training_POS.txt"
	file_NER = read_property('FineOutputfilesPath') + label + "_training_NER.txt"
	file_Chunk = read_property('FineOutputfilesPath') + label + "_training_Chunk.txt"
	################################################## TRAINING##############################################

	#########################  BAG OF WORDS  ################################
	print "Training"
	f1 = open(file_word, "r")
	corpus = []
	for lines in f1:
		l = lines.split()
		words = ""
		for w in l:
			words = words + w + " "
		corpus.append(words)		
	vectorizer_words = CountVectorizer(min_df=1, ngram_range=(1, 2))
	X_words = vectorizer_words.fit_transform(corpus)
	f1.close()
	print "word feature extraction done"

	#########################  BAG OF WORDS OF POS ################################
	f2 = open(file_POS, "r")
	corpus = []
	for lines in f2:
		l = lines.split()
		words = ""
		for w in l:
			words = words + w + " "
		corpus.append(words)		
	vectorizer_POS = CountVectorizer(min_df=1, ngram_range=(1, 2))
	X_POS = vectorizer_POS.fit_transform(corpus)
	f2.close()
	print "POS feature extraction done"

	#########################  BAG OF WORDS OF NER ################################
	f3 = open(file_NER, "r")
	corpus = []
	for lines in f3:
		l = lines.split()
		words = ""
		for w in l:
			words = words + w + " "
		corpus.append(words)		
	vectorizer_NER = CountVectorizer(min_df=1, ngram_range=(1, 2))
	X_NER = vectorizer_NER.fit_transform(corpus)
	f3.close()
	print "NER feature extraction done"

	#########################  BAG OF WORDS OF Chunks ################################
	f4 = open(file_Chunk, "r")
	corpus = []
	for lines in f4:
		l = lines.split()
		words = ""
		for w in l:
			words = words + w + " "
		corpus.append(words)		
	vectorizer_Chunk = CountVectorizer(min_df=1, ngram_range=(1, 2))
	X_Chunk = vectorizer_Chunk.fit_transform(corpus)
	f4.close()
	print "Chunk feature extraction done"

	X = hstack((X_words, X_POS))
	X_train = hstack((X, X_NER))
	X_train = hstack((X_train, X_Chunk))

	################################################## TESTING ##############################################
	
	#########################  BAG OF WORDS  ################################
	print "Testing"
	corpus = []
	words = ""
	l = line.split()
	for w in l:
		words = words + w + " "
	corpus.append(words)		
	X_words = vectorizer_words.transform(corpus)
	print "word feature extraction for test done "

	#########################  BAG OF WORDS OF POS ################################
	corpus = []
	text = nltk.word_tokenize(line)
        pos_seq = nltk.pos_tag(text)
        pos_tags = ""
        for pos in pos_seq:
		pos_tags = pos_tags + pos[1] + " "
        corpus.append(pos_tags)
	X_POS = vectorizer_POS.transform(corpus)
	print "POS feature extraction for test done"

	#########################  BAG OF WORDS OF NER ################################
	corpus = []
	ner = st.tag(line.split())
        ner_tag = ""
        for n in ner:
		ner_tag = ner_tag + n[1] + " "
        corpus.append(ner_tag)
	X_NER = vectorizer_NER.transform(corpus)
	print "NER feature extraction for test done"

	#########################  BAG OF WORDS OF Chunks ################################
	corpus = []
	chunks = annotator.getAnnotations(line)['chunk']
        chunk = ""
        for elem in chunks:
		chunk = chunk + elem[1] + " "
        corpus.append(chunk)
	X_Chunk = vectorizer_Chunk.transform(corpus)
	print "Chunk feature extraction for test done done"

	X = hstack((X_words, X_POS))
	X_test = hstack((X, X_NER))
	X_test = hstack((X_test, X_Chunk))
	
###################################### Applying the LinearSVC Classifier ################################################

# 	print "Applying SVC"
# 	self = LinearSVC(loss='l2', dual=False, tol=1e-3)
# 	self = LinearSVC.fit(self, X_train, train_class)
# 	test_class = LinearSVC.predict(self, X_test)
	test_class_top5 = naiveBayes.naiveBayesTop5ClassLabels(X_train, train_class, X_test)
	
	t_class_each = []
	for testClass in test_class_top5:
		t_class_each.append(label + ":" + testClass)
	print row
	row = row + 1
	t_class.append(t_class_each)
	print t_class_each

fi.close()
f.close()

###################################### Accuracy Calculation ################################################

with open('predictedfineLabel5', 'wb') as f:
    pickle.dump(t_class, f)
print "--------------a-------------------------"
test_class_gold = []
f = open(read_property('testfilepath'), 'r')
for lines in f:
	test_class_gold.append(lines.split()[0])
print t_class
print test_class_gold
print len(t_class)
print len(test_class_gold)
hits = 0.00
for i in range(0, len(t_class)):
	for testLabel in t_class[i]:
		if testLabel == test_class_gold[i]:
			print testLabel
			hits = hits + 1
print "Number of hits = ", hits
print "The accuracy is ", ((hits / len(t_class)) * 100.0), " %"

