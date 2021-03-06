import commands, random, operator
from collections import defaultdict

def classify(test_file, model_file, classified_file):
  return commands.getoutput('../bin/svm_classify %s %s %s' % (test_file, model_file, classified_file))
  
def learn(train_file, model_file, c=None, j=None):
  c_string = ""
  if c:
    c_string = "-c %s " % c
  j_string = ""
  if j:
    j_string = "-j %s " % j
  # print 'svm_learn %s%s%s %s' % (c_string, j_string, train_file, model_file)
  return commands.getoutput('../bin/svm_learn %s%s%s %s' % (c_string, j_string, train_file, model_file))
  
def get_accuracy(stringy):
  stringy = stringy.split('\n')
  for s in stringy:
    if 'Accuracy' in s:
      nums = s.split(':')[1]
      pct, rest = nums.split('% (')
      num_correct, rest = rest.split(' correct,')
      num_incorrect, rest = rest.split(' incorrect,')
      return (float(pct), int(num_correct), int(num_incorrect))
  raise Exception('Couldn\'t find accuracy string')
  
def split_for_validation(example_file, num=10, randomize=True):
  with open(example_file, 'r') as f:
    lines = f.readlines()
  if randomize:
    random.shuffle(lines)
  size = len(lines) / num
  for i in range(0, num):
    with open("%s.%d.tr" % (example_file, i), 'w') as f:
      with open("%s.%d.va" % (example_file, i), 'w') as f2:
        for j in range(0, len(lines)):
          if j % num != i:
            f.write(lines[j])
          else:
            f2.write(lines[j])

def get_cross_val_accuracy(train_file, num=10, c=None, j=None, verbose=False):
  split_for_validation(train_file, num)
  accuracies = []
  for i in range(0, num):
    learn("%s.%d.tr" % (train_file, i), "%s.%d.tr.mod" % (train_file, i), c, j)
    accuracies.append(get_accuracy(classify("%s.%d.va" % (train_file, i), "%s.%d.tr.mod" % (train_file, i), "%s.%d.tr.cls" % (train_file, i))))
    # print get_false_posneg("%s.%d.va" % (train_file, i), "%s.%d.tr.cls" % (train_file, i))
  cc, ic = 0, 0
  for _, c, i in accuracies:
    cc += c
    ic += i
  if verbose:
    print accuracies
  return (float(cc)/(cc+ic), cc, ic)
  
def get_false_posneg(test_file, classified_file):
  false_pos, false_neg = 0, 0
  f, cf = open(test_file, 'r'), open(classified_file, 'r')
  for l in f:
    f_val = int(l.replace('\n','').split(' ', 2)[0])
    cf_val = float(cf.readline().replace('\n',''))
    if f_val * cf_val < 0:
      if cf_val < 0:
        false_neg += 1
      else:
        false_pos += 1
  f.close()
  cf.close()
  return (false_pos, false_neg)
  
def get_separating_hyperplane(model_file):
  i, b, w = 0, 0.0, defaultdict(float)
  with open(model_file, 'r') as f:
    for l in f:
      if i == 1 and not '0' in l and not 'kernel type' in l:
          raise Exception("Not a linear kernel or not a model file.")
      elif i == 10:
        b = float(l.split('#', 1)[0])
      elif i > 10:
        alpha, fvs = l.split(' ', 1)
        alpha, fvs = float(alpha), fvs.split('#', 1)[0].strip().split(' ')
        #print alpha
        for fv in fvs:
          f, v = fv.split(':')
          #print f, v
          w[int(f)] += float(v) * alpha
      i += 1
  return (sorted(w.iteritems(), key=operator.itemgetter(1)), b)
  
# print get_separating_hyperplane('../examples_tfidf.txt.9.tr.mod')