

USAGE = """Basic grading script for CS143B virtual memory project.  Compares students output files with the expected ones
one output 'test case' at a time, generates a score for each file, and outputs those grades to a .csv file:

Expected args:
 1: expected outputs for non-TLB
 2: expected outputs for TLB
 3: submissions directory with files of format 13523465.txt or 1342355_tlb.txt  (use the parsing checker so they format properly!)
"""

import os
import sys
import csv

def parse_output(fname):
    with open(fname) as f:
        data = f.readlines()

    # XXX: remove blank lines
    data = [l for l in data if l]
    assert len(data) == 1, "# lines in file %s not 1! got %d" % (fname, len(data))

    results = data[0].split()
    assert len(results), "empty results! got: %s" % results

    return results


def sid_from_fname(fname):
    fname = os.path.split(fname)[-1]
    fname = fname.replace('.txt', '')
    fname = fname.replace('_tlb', '')
    return fname


def is_tlb_submission(fname):
    return '_tlb' in fname.lower()


def grade_file(fname):
    sid = sid_from_fname(fname)

    results = parse_output(fname)
    # print 'sid:', sid, 'fname:', fname, 'results:', results

    exp_results = exp_output_tlb if is_tlb_submission(fname) else exp_output
    score = sum(first == second for first, second in zip(results, exp_results))

    return score


final_grades = dict()
def record_score(fname, score):
    # global final_grades
    sid = sid_from_fname(fname)
    grade = final_grades.get(sid, [None, None])
    is_tlb = is_tlb_submission(fname)
    idx = 1 if is_tlb else 0

    if grade[idx] is not None:
        print "WARNING: changing grade from %s to %f" % (grade[idx], score)

    grade[idx] = score
    final_grades[sid] = grade


def output_score(out_fname):
    out_grades = [[sid, str(grade[0]), str(grade[1])] for sid, grade in final_grades.items()]

    with open(out_fname, 'wb') as csv_f:
        writer = csv.writer(csv_f)
        for line in out_grades:
            writer.writerow(line)

    # print "wrote lines to file:"

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print

    # 31 test cases = 31 outputs
    global exp_output
    exp_output = sys.argv[1]
    exp_output = parse_output(exp_output)
    max_points = len(exp_output)

    # 62 outputs expected
    global exp_output_tlb
    exp_output_tlb = sys.argv[2]
    exp_output_tlb = parse_output(exp_output_tlb)
    max_points_tlb = len(exp_output_tlb)

    subs_dir = sys.argv[3]
    for fname in os.listdir(subs_dir):
        # test by checking expected results output with itself: this is max points!
        # fname = sys.argv[2]

        fname = os.path.join(subs_dir, fname)
        score = grade_file(fname)
        this_max_pts = max_points_tlb if is_tlb_submission(fname) else max_points

        record_score(fname, score)

        ## output some summary of results for checking:
        if score > this_max_pts:
            print "WARNING: got more than possible score!"
        elif score == 0:
            print "ZERO SCORE submission:", fname
        elif score < this_max_pts/2:
            print "SCORE less than half:", fname
        else:
            continue
            # print score, '/', this_max_pts

    print "FINAL GRADES:"
    from pprint import pprint
    pprint(final_grades)

    out_fname = "grades.csv"
    output_score(out_fname)