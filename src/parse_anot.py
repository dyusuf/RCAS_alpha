def check_argv(argv, handler):

    usage = """
    parse_anot.py

    version: 0.0.2
    author: Dilmurat Yusuf

    Usage:

    $ parse_anot.py < bedtools_output > annotation_in_BED_format

    $ bedtools_upstream_process ... | parse_anot.py > annotation_in_BED_format

    The following parameters should be used in bedtools_upstream_process:
    bedtools intersect -b reference_in_gff3 -a coordinates_in_BED -wao

    The format is tab delimited bed format and
    output consists of following columns:
    chromosome_id, start_position, end_position,
    seq_id, score, strand, feature, feature_id, gene_id,
    transcript_id, gene_type, gene_name, gene_strand, overlap_number, weight

    The reported features include exon, UTR5/3, CDS, intron and intergenic.

    For a coordinate which is assocaited with a transcript_id
    but NOT with exons, it is annotated as intron.

    For a coordiate which is NOT assocaited with a genes_id,
    it is annotated as intergenic.
    """

    try:
        opts, args = getopt.getopt(argv, "h", [""])

    except getopt.GetoptError:
        print(usage)
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()

    # if there is input data, the connection to tty (terminal) will be False
    tty = handler.isatty()
    if tty is True:
        print(usage)
        sys.exit()


def process_cor_line(line):
    # process each line,
    # return coordinate info & feature infos

    line = line.strip().split("\t")
    cor_info = "\t".join(line[:6])
    anot_info = [line[8], line[12], line[-2], line[-1]]

    """ determine feature of annotation.
    check if ID is present.
    it is always true in GENCODE foramt,
    but it varies in ENSEMBL format.
    use feature in ID field if it is cotained in the field.
    by this way, it can conform feature annotations
    between GENCODE and ENSEMBL
    that feature annotation sush as
    "processed_transcript" etc. will be exluded,
    instead to use "transcript" for both annotations."""
    if anot_info[2].startswith("ID="):
        ID = anot_info[2].split(";")[0]
        if ":" in ID:
            feature = ID.split(":")[0].replace("ID=", "")
            anot_info[0] = feature

    return cor_info, anot_info


def iterate_list(elements, tag):
    return [ele for ele in elements if tag in ele]


def extract_info(cor_anot):
    # extract cor_info, feature_info, child_id, parent_id

    child_id = "None"
    parent_id = "None"

    cor_info, anot_info = cor_anot
    feature_info = anot_info[-2]
    anot_info, overlap_number = anot_info[:-1], anot_info[-1]
    # overlap_number is conditioned to cor_info and anot_info
    cor_info = "%s\t%s" % (cor_info, overlap_number)

    feature = anot_info[0]

    if feature_info != '.':

        infos = feature_info.split(";")

        """Contrary to GENCODE gff3 format,
        which uses constant fields and order in each line,
        ENSEMBL gff3 format varies in both respects.
        Therefore, instead of acessing values vi index,
        I use iterate_list to locate
        value with given key (tag).""
        """

        if "Parent=" not in feature_info:
            parent_id = "None"
        else:
            parent = iterate_list(infos, "Parent=")[0]
            parent_id = parent.replace("Parent=", "")

        try:
            child_id = iterate_list(infos, "ID=")[0].split("=")[1]
        except:
            try:
                child_id = iterate_list(infos, "exon_id=")[0].split("=")[1]
            except:
                child_id = feature + ":" + parent_id.split(":")[-1]

    if feature == "transcript":
        try:
            gene_type = iterate_list(infos, "gene_type=")[0].split("=")[1]
        except:
            gene_type = iterate_list(infos, "biotype=")[0].split("=")[1]

        try:
            gene_name = iterate_list(infos, "gene_name=")[0].split("=")[1]
        except:
            gene_name = iterate_list(infos, "Name=")[0].split("=")[1]

        gene_id = parent_id

        id_description[child_id] = [gene_id,
                                    gene_type, gene_name]

    return cor_info, anot_info, child_id, parent_id


def update_child_and_parent(child_id, parent_id, child_and_parent):
    if child_id not in child_and_parent:
            child_and_parent[child_id] = parent_id

    return child_and_parent


def update_id_and_info(child_id, anot_info, id_and_info):
    if child_id not in id_and_info:
            id_and_info[child_id] = anot_info

    return id_and_info


def update_cor_and_ids(child_id, cor_info, cor_and_ids):
    try:
        cor_and_ids[cor_info].add(child_id)
    except:
        """use set to remove unwanted techinical duplicates
        which input file can contain"""
        cor_and_ids[cor_info] = set([child_id])

    return cor_and_ids


def substract_parent_id(child_ids, child_and_parent):

    parent_ids = set([])

    for child_id in child_ids:
        parent_id = child_and_parent[child_id]
        parent_ids.add(parent_id)

    child_ids = child_ids - parent_ids

    return child_ids


def substract_parent_exon(child_ids):

    # collect child_ids which are associate with identical exon_id
    exon_features = {}
    for child_id in child_ids:
        if ":" in child_id:
            exon_id = ":".join(child_id.split(":")[1:])

            try:
                exon_features[exon_id].append(child_id)
            except:
                exon_features[exon_id] = [child_id]

    # collect exon_ids that are co-present with UTR and CDS
    exon_set = []
    for feature_ids in exon_features.values():
        """ example of feature_ids
        ['exon:ENST00000483335.1:3'],
        the case of no CDS or UTR documentation in reference
        ['exon:ENST00000287078.6:2', 'CDS:ENST00000287078.6:2']
        """

        if len(feature_ids) > 1:
            for child_id in feature_ids:
                feature = child_id.split(":")[0]
                if feature in ('exon'):
                    exon_set.append(child_id)

    child_ids = child_ids - set(exon_set)

    return child_ids


def extract_feature(anot_info, child_id, child_and_parent, id_description):

    feature = anot_info[0]
    strand = anot_info[1]

    if feature == ".":
        feature = "intergenic"
        feature_id = "unknown"
        gene_id = "unknown"
        transcript_id = "unknown"
        gene_type = "unknown"
        gene_name = "unknown"
        strand = "*"

    else:
        feature_id = child_id

        if feature == "transcript":
            transcript_id = feature_id
        else:
            transcript_id = child_and_parent[feature_id]

        feature_description = id_description[transcript_id]

        transcript_id = transcript_id.replace("transcript:", "")

        gene_id = feature_description[0].replace("gene:", "")
        gene_type = feature_description[1]
        gene_name = feature_description[2]

        if feature == "transcript":
            feature = "intronic"

        if feature == "UTR":
            feature = feature_id.split(":")[0]

    return "\t".join([feature, feature_id, gene_id,
                     transcript_id, gene_type,
                     gene_name, strand])


def update_table(cor_info, child_ids, id_and_info,
                 child_and_parent,
                 id_description, table):

    weight = 1. / len(child_ids)

    for child_id in child_ids:
        anot_info = id_and_info[child_id]

        feature_info = extract_feature(anot_info, child_id,
                                       child_and_parent,
                                       id_description)

        table.append("%s\t%f\t%s" % (cor_info, weight, feature_info))

    return table

if __name__ == '__main__':
    import sys
    import getopt

    argv = sys.argv[1:]
    handler = sys.stdin

    # check commandline options
    check_argv(argv, handler)

    """ extract coordinate info & feature infos.
    for the case of gff3 from ENSEMBLE,
    since it cotains ID=chromosome,
    I provide control to remove such line."""
    cor_anot_list = [process_cor_line(line)
                     for line in handler
                     if "ID=chromosome:" not in line]

    # build dictionary between child_id and parent_id
    # defined in gene:transcript:exon
    child_and_parent = {}

    # build dictionary between child_id and complete anot info
    id_and_info = {}

    # build dictionary between coordinate info and list of associated ids
    cor_and_ids = {}

    # build dictionary between transcript_id and feature description
    id_description = {}

    # update child_and_parent, id_and_info, cor_and_ids, id_description
    for cor_anot in cor_anot_list:
        cor_info, anot_info, child_id, parent_id = extract_info(cor_anot)

        child_and_parent = update_child_and_parent(child_id, parent_id,
                                                   child_and_parent)

        cor_and_ids = update_cor_and_ids(child_id, cor_info, cor_and_ids)

        id_and_info = update_id_and_info(child_id, anot_info, id_and_info)

    # remove duplicate representation (gene:transcript:exon) in a gene model
    for cor, child_ids in cor_and_ids.items():

        if child_ids != set(["None"]):

            # for each coordinate,
            # substract associated parent ids defined in gene:transcript:exon
            child_ids = substract_parent_id(child_ids, child_and_parent)

            """for each coordinate,
            substract associated parent exon ids
            defined in exon:CDS or exon:UTR.
            unfortunately in gencode gff3,
            the relation is not explict between exon and CDS or UTR
            that's why it can not be implemented by substract_parent_id()"""
            # the function substract_parent_exon() is switched off,
            # since even though it is easy for GENCODE gff3 format,
            # there is no way to trace relation between exons and CDS/UTR
            # in the format of ENSEMBLE gff3
            # child_ids = substract_parent_exon(child_ids)

            cor_and_ids[cor] = child_ids

    # generate table
    header = ("chromosome_id\tstart_position" +
              "\tend_position\tseq_id\tscore\tstrand\toverlap_number" +
              "\tweight\tfeature\tfeature_id\tgene_id\ttranscript_id" +
              "\tgene_type\tgene_name\tgene_strand")
    table = [header]
    for cor_info, child_ids in cor_and_ids.items():
        table = update_table(cor_info, child_ids, id_and_info,
                             child_and_parent, id_description,
                             table)

    print("\n".join(table))
