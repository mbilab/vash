from datetime import datetime

from django.contrib.auth.models import Group, User
from django.db import models

# Create your models here.


class CohortModel(models.Model):
    ctime = models.DateTimeField(auto_now_add=True)
    info = models.TextField(null=True)
    name = models.TextField(null=True)
    n_variants = models.IntegerField(null=True)
    samples = models.TextField(null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_group = models.ForeignKey(
        Group, null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)
    queries = models.TextField(null=True)
    pid = models.TextField(null=True)
    token = models.TextField(null=True)
    others = models.TextField(null=True)
    available = models.TextField(null=True)
    parent_cohort_id = models.TextField(null=True)
    created_percentage = models.FloatField(null=True)

    def save_filter(self, token, query_str, qs):
        self.ctime = datetime.now()
        self.name += ' (filtered)'
        self.n_variants = None
        self.created_precentage = 1
        self.pk = None
        self.queries = query_str
        self.token = token
        self.save()

    def has_parent(self):
        return not self.parent_cohort_id == None

    def is_owned_by(self, user):
        return self.owner == user

    def parent_is_owned_by(self, user):
        return (not self.has_parent()) or CohortModel.objects.get(id=self.parent_cohort_id).owner == user

    class Meta:
        ordering = ('id',)


class AAChange_dot_knownGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class AAChange_dot_refGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class ANNOVAR_DATETerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class CLNDISDBTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class CLNDNTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class CLNREVSTATTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class CLNSIGTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class ExonicFunc_dot_knownGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class ExonicFunc_dot_refGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class FATHMM_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class Func_dot_knownGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class Func_dot_refGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class GeneDetail_dot_knownGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class GeneDetail_dot_refGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class Gene_dot_knownGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class Gene_dot_refGeneTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class Geno2MPTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class LRT_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class M_dash_CAP_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class MetaLR_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class MetaSVM_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class MutationTaster_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class PROVEAN_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class Polyphen2_HDIV_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class Polyphen2_HVAR_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class SIFT_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class culpritTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class fathmm_dash_MKL_coding_predTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class avsnp150Terms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class variantIDTerms(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)
    term = models.TextField(null=True)


class VariantModel(models.Model):
    cohort = models.ForeignKey(CohortModel, on_delete=models.CASCADE)

    # basic
    CHROM = models.CharField(max_length=5, null=True, db_index=True)
    POS = models.TextField(null=True)
    Start = models.IntegerField(null=True, db_index=True)
    End = models.IntegerField(null=True, db_index=True)
    REF = models.TextField(null=True)
    ALT = models.TextField(null=True)
    Others = models.TextField(null=True)
    FORMAT = models.TextField(null=True)
    variantID = models.TextField(null=True)  # ! check to rename
    # rsID = models.TextField(null=True)
    Samples = models.TextField(null=True)
    Genotype = models.TextField(null=True)

    # gene info
    MostImportantGeneFeature = models.TextField(null=True)
    MostImportantFeatureGene = models.TextField(null=True)
    n_variants = models.IntegerField(null=True)
    GeneDescription = models.TextField(null=True)

    # genotype number
    AllRefHomGtyNum = models.IntegerField(null=True)
    AllHetGtyNum = models.IntegerField(null=True)
    AllAltHomGtyNum = models.IntegerField(null=True)
    AffectedRefHomGtyNum = models.IntegerField(null=True)
    AffectedHetGtyNum = models.IntegerField(null=True)
    AffectedAltHomGtyNum = models.IntegerField(null=True)
    UnaffectedRefHomGtyNum = models.IntegerField(null=True)
    UnaffectedHetGtyNum = models.IntegerField(null=True)
    UnaffectedAltHomGtyNum = models.IntegerField(null=True)

    # frequency
    MaxDBAltAF = models.FloatField(null=True)
    altFreq_at_exacEAS = models.FloatField(null=True)
    altFreq_at_exacSAS = models.FloatField(null=True)
    altFreq_at_1kgeas201305 = models.FloatField(null=True)
    altFreq_at_1kgsas201305 = models.FloatField(null=True)
    altFreq_at_gnomad_dot_exomeEAS = models.FloatField(null=True)
    altFreq_at_gnomad_dot_exomeSAS = models.FloatField(null=True)
    altFreq_at_gnomad_dot_genomeEAS = models.FloatField(null=True)

    # quality
    QUAL = models.FloatField(null=True)
    FILTER = models.TextField(null=True)

    # Others
    OthersInfo = models.TextField(null=True)

    # score1
    ada_score_at_dbscSNV = models.TextField(null=True)  # score
    GERPpp_RS = models.TextField(null=True)
    clinvar_clnsig = models.TextField(null=True)
    clinvar_trait = models.TextField(null=True)
    clinvar_golden_stars = models.TextField(null=True)
    DiseaseCausalProb_ExoVarTrainedModel = models.TextField(
        null=True)  # Logistic
    IsRareDiseaseCausal_ExoVarTrainedModel = models.TextField(null=True)
    BestCombinedTools_OptimalCutoff_TP_TN = models.TextField(null=True)
    MutationTaster_pred = models.TextField(null=True)
    MutationTaster_score = models.FloatField(null=True)
    MutationAssessor_pred = models.TextField(null=True)
    MutationAssessor_score = models.FloatField(null=True)

    # score2
    MutPred_Top5features = models.TextField(null=True)
    MutPred_score = models.FloatField(null=True)
    Eigen_phred = models.TextField(null=True)

    # uniprot
    UniProtFeatureForRefGene = models.TextField(null=True)
    UniProtFeatureForGEncode = models.TextField(null=True)
    UniProtFeatureForKnownGene = models.TextField(null=True)

    # not in client
    Pseudogenes = models.TextField(null=True)
    DiseaseName_s_MIMid = models.TextField(null=True)
    GeneMIMid = models.TextField(null=True)
    DGVIDs = models.TextField(null=True)
    CNVSampleSize = models.TextField(null=True)
    LossCNV = models.TextField(null=True)
    GainCNV = models.TextField(null=True)
    MousePhenotypeMGI = models.TextField(null=True)
    MousePhenotypeIMPC = models.TextField(null=True)
    ZebrafishPhenotype = models.TextField(null=True)
    DDDPhenotype = models.TextField(null=True)
    COSMICCancerInfo = models.TextField(null=True)

    # for ANNOVAR
    AC = models.FloatField(null=True)
    AF = models.FloatField(null=True)
    AN = models.FloatField(null=True)
    BaseQRankSum = models.FloatField(null=True)
    ClippingRankSum = models.FloatField(null=True)
    DP = models.FloatField(null=True)
    END_flag = models.FloatField(null=True)
    ExcessHet = models.FloatField(null=True)
    FS = models.FloatField(null=True)
    InbreedingCoeff = models.FloatField(null=True)
    MLEAC = models.FloatField(null=True)
    MLEAF = models.FloatField(null=True)
    MQ = models.FloatField(null=True)
    MQRankSum = models.FloatField(null=True)
    QD = models.FloatField(null=True)
    ReadPosRankSum = models.FloatField(null=True)
    SOR = models.FloatField(null=True)
    VQSLOD = models.FloatField(null=True)
    culprit = models.TextField(null=True)
    ANNOVAR_DATE = models.TextField(null=True)
    Func_dot_refGene = models.TextField(null=True)
    Gene_dot_refGene = models.TextField(null=True)
    GeneDetail_dot_refGene = models.TextField(null=True)
    ExonicFunc_dot_refGene = models.TextField(null=True)
    AAChange_dot_refGene = models.TextField(null=True)
    Func_dot_knownGene = models.TextField(null=True)
    Gene_dot_knownGene = models.TextField(null=True)
    GeneDetail_dot_knownGene = models.TextField(null=True)
    ExonicFunc_dot_knownGene = models.TextField(null=True)
    AAChange_dot_knownGene = models.TextField(null=True)
    CLNALLELEID = models.FloatField(null=True)
    CLNDN = models.TextField(null=True)
    CLNDISDB = models.TextField(null=True)
    CLNREVSTAT = models.TextField(null=True)
    CLNSIG = models.TextField(null=True)
    avsnp150 = models.TextField(null=True)
    esp6500siv2_all = models.FloatField(null=True)  # !
    tbbaf_all = models.FloatField(null=True)
    tbbaf_illumina = models.FloatField(null=True)
    tbbaf_proton = models.FloatField(null=True)
    N_1000g2015aug_all = models.FloatField(null=True)
    EAS_dot_sites_dot_2015_08 = models.FloatField(null=True)  # !
    AFR_dot_sites_dot_2015_08 = models.FloatField(null=True)
    AMR_dot_sites_dot_2015_08 = models.FloatField(null=True)
    EUR_dot_sites_dot_2015_08 = models.FloatField(null=True)
    SAS_dot_sites_dot_2015_08 = models.FloatField(null=True)
    ExAC_ALL = models.FloatField(null=True)
    ExAC_AFR = models.FloatField(null=True)
    ExAC_AMR = models.FloatField(null=True)
    ExAC_EAS = models.FloatField(null=True)
    ExAC_FIN = models.FloatField(null=True)
    ExAC_NFE = models.FloatField(null=True)
    ExAC_OTH = models.FloatField(null=True)
    ExAC_SAS = models.FloatField(null=True)
    cg69 = models.FloatField(null=True)
    Kaviar_AF = models.FloatField(null=True)
    Kaviar_AC = models.FloatField(null=True)
    Kaviar_AN = models.FloatField(null=True)
    AF_popmax = models.FloatField(null=True)
    AF_male = models.FloatField(null=True)
    AF_female = models.FloatField(null=True)
    AF_raw = models.FloatField(null=True)
    AF_afr = models.FloatField(null=True)
    AF_sas = models.FloatField(null=True)
    AF_amr = models.FloatField(null=True)
    AF_eas = models.FloatField(null=True)
    AF_nfe = models.FloatField(null=True)
    AF_fin = models.FloatField(null=True)
    AF_asj = models.FloatField(null=True)
    AF_oth = models.FloatField(null=True)
    non_topmed_AF_popmax = models.FloatField(null=True)
    non_neuro_AF_popmax = models.FloatField(null=True)
    non_cancer_AF_popmax = models.FloatField(null=True)
    controls_AF_popmax = models.FloatField(null=True)
    gnomAD_genome_ALL = models.FloatField(null=True)
    gnomAD_genome_AFR = models.FloatField(null=True)
    gnomAD_genome_AMR = models.FloatField(null=True)
    gnomAD_genome_ASJ = models.FloatField(null=True)
    gnomAD_genome_EAS = models.FloatField(null=True)
    gnomAD_genome_FIN = models.FloatField(null=True)
    gnomAD_genome_NFE = models.FloatField(null=True)
    gnomAD_genome_OTH = models.FloatField(null=True)
    gnomAD_exome_ALL = models.FloatField(null=True)
    gnomAD_exome_AFR = models.FloatField(null=True)
    gnomAD_exome_AMR = models.FloatField(null=True)
    gnomAD_exome_ASJ = models.FloatField(null=True)
    gnomAD_exome_EAS = models.FloatField(null=True)
    gnomAD_exome_FIN = models.FloatField(null=True)
    gnomAD_exome_NFE = models.FloatField(null=True)
    gnomAD_exome_OTH = models.FloatField(null=True)
    gnomAD_exome_SAS = models.FloatField(null=True)
    gnomAD_2_exome_AF = models.FloatField(null=True)
    gnomAD_2_exome_AF_afr = models.FloatField(null=True)
    gnomAD_2_exome_AF_amr = models.FloatField(null=True)
    gnomAD_2_exome_AF_asj = models.FloatField(null=True)
    gnomAD_2_exome_AF_eas = models.FloatField(null=True)
    gnomAD_2_exome_AF_female = models.FloatField(null=True)
    gnomAD_2_exome_AF_fin = models.FloatField(null=True)
    gnomAD_2_exome_AF_male = models.FloatField(null=True)
    gnomAD_2_exome_AF_nfe = models.FloatField(null=True)
    gnomAD_2_exome_AF_oth = models.FloatField(null=True)
    gnomAD_2_exome_AF_popmax = models.FloatField(null=True)
    gnomAD_2_exome_AF_raw = models.FloatField(null=True)
    gnomAD_2_exome_AF_sas = models.FloatField(null=True)
    gnomAD_2_exome_controls_AF_popmax = models.FloatField(null=True)
    gnomAD_2_exome_non_cancer_AF_popmax = models.FloatField(null=True)
    gnomAD_2_exome_non_neuro_AF_popmax = models.FloatField(null=True)
    gnomAD_2_exome_non_topmed_AF_popmax = models.FloatField(null=True)
    gnomAD_2_genome_AF = models.FloatField(null=True)
    gnomAD_2_genome_AF_afr = models.FloatField(null=True)
    gnomAD_2_genome_AF_amr = models.FloatField(null=True)
    gnomAD_2_genome_AF_asj = models.FloatField(null=True)
    gnomAD_2_genome_AF_eas = models.FloatField(null=True)
    gnomAD_2_genome_AF_female = models.FloatField(null=True)
    gnomAD_2_genome_AF_fin = models.FloatField(null=True)
    gnomAD_2_genome_AF_male = models.FloatField(null=True)
    gnomAD_2_genome_AF_nfe = models.FloatField(null=True)
    gnomAD_2_genome_AF_oth = models.FloatField(null=True)
    gnomAD_2_genome_AF_popmax = models.FloatField(null=True)
    gnomAD_2_genome_AF_raw = models.FloatField(null=True)
    gnomAD_2_genome_AF_sas = models.FloatField(null=True)
    gnomAD_2_genome_controls_AF_popmax = models.FloatField(null=True)
    gnomAD_2_genome_non_cancer_AF_popmax = models.FloatField(null=True)
    gnomAD_2_genome_non_neuro_AF_popmax = models.FloatField(null=True)
    gnomAD_2_genome_non_topmed_AF_popmax = models.FloatField(null=True)
    tbbaf = models.FloatField(null=True)
    Geno2MP = models.TextField(null=True)
    SIFT_score = models.FloatField(null=True)
    SIFT_converted_rankscore = models.FloatField(null=True)
    SIFT_pred = models.TextField(null=True)
    Polyphen2_HDIV_pred = models.TextField(null=True)
    Polyphen2_HDIV_score = models.FloatField(null=True)
    Polyphen2_HDIV_rankscore = models.FloatField(null=True)
    Polyphen2_HVAR_score = models.FloatField(null=True)
    Polyphen2_HVAR_rankscore = models.FloatField(null=True)
    Polyphen2_HVAR_pred = models.TextField(null=True)
    LRT_score = models.FloatField(null=True)
    LRT_converted_rankscore = models.FloatField(null=True)
    LRT_pred = models.TextField(null=True)
    MutationTaster_score = models.FloatField(null=True)
    MutationTaster_converted_rankscore = models.FloatField(null=True)
    MutationTaster_pred = models.TextField(null=True)
    MutationAssessor_score = models.FloatField(null=True)
    MutationAssessor_score_rankscore = models.FloatField(null=True)
    MutationAssessor_pred = models.TextField(null=True)
    FATHMM_score = models.FloatField(null=True)
    FATHMM_converted_rankscore = models.FloatField(null=True)
    FATHMM_pred = models.TextField(null=True)
    PROVEAN_score = models.FloatField(null=True)
    PROVEAN_converted_rankscore = models.FloatField(null=True)
    PROVEAN_pred = models.TextField(null=True)
    VEST3_score = models.FloatField(null=True)
    VEST3_rankscore = models.FloatField(null=True)
    MetaSVM_score = models.FloatField(null=True)
    MetaSVM_rankscore = models.FloatField(null=True)
    MetaSVM_pred = models.TextField(null=True)
    MetaLR_score = models.FloatField(null=True)
    MetaLR_rankscore = models.FloatField(null=True)
    MetaLR_pred = models.TextField(null=True)
    M_dash_CAP_score = models.FloatField(null=True)
    M_dash_CAP_rankscore = models.FloatField(null=True)
    M_dash_CAP_pred = models.TextField(null=True)
    CADD_raw = models.FloatField(null=True)
    CADD_raw_rankscore = models.FloatField(null=True)
    CADD_phred = models.FloatField(null=True)
    DANN_score = models.FloatField(null=True)
    DANN_rankscore = models.FloatField(null=True)
    fathmm_dash_MKL_coding_score = models.FloatField(null=True)
    fathmm_dash_MKL_coding_rankscore = models.FloatField(null=True)
    fathmm_dash_MKL_coding_pred = models.TextField(null=True)
    Eigen_coding_or_noncoding = models.TextField(null=True)  # !
    Eigen_dash_raw = models.FloatField(null=True)  # !
    Eigen_dash_PC_dash_raw = models.FloatField(null=True)  # !
    GenoCanyon_score = models.FloatField(null=True)
    GenoCanyon_score_rankscore = models.FloatField(null=True)
    integrated_fitCons_score = models.FloatField(null=True)
    integrated_fitCons_score_rankscore = models.FloatField(null=True)
    integrated_confidence_value = models.FloatField(null=True)
    GERPpp_RS = models.FloatField(null=True)
    GERPpp_RS_rankscore = models.FloatField(null=True)
    phyloP100way_vertebrate = models.FloatField(null=True)
    phyloP100way_vertebrate_rankscore = models.FloatField(null=True)
    phyloP20way_mammalian = models.FloatField(null=True)
    phyloP20way_mammalian_rankscore = models.FloatField(null=True)
    phastCons100way_vertebrate = models.FloatField(null=True)
    phastCons100way_vertebrate_rankscore = models.FloatField(null=True)
    phastCons20way_mammalian = models.FloatField(null=True)
    phastCons20way_mammalian_rankscore = models.FloatField(null=True)
    SiPhy_29way_logOdds = models.FloatField(null=True)
    SiPhy_29way_logOdds_rankscore = models.FloatField(null=True)
    Interpro_domain = models.TextField(null=True)  # !
    GTEx_V6_gene = models.TextField(null=True)  # !
    GTEx_V6_tissue = models.TextField(null=True)  # !
    dbscSNV_ADA_SCORE = models.FloatField(null=True)
    dbscSNV_RF_SCORE = models.FloatField(null=True)
    GWAVA_region_score = models.FloatField(null=True)
    GWAVA_tss_score = models.FloatField(null=True)
    GWAVA_unmatched_score = models.FloatField(null=True)
    tfbsConsSites = models.TextField(null=True)  # !
    wgRna = models.TextField(null=True)  # !
    targetScanS = models.TextField(null=True)  # !

    class Meta:
        ordering = ['id']


class HashCodeModel(models.Model):
    variant = models.ForeignKey(VariantModel, on_delete=models.CASCADE)

    variantID = models.CharField(max_length=25, null=True, db_index=True)
    Func_dot_refGene = models.CharField(
        max_length=25, null=True, db_index=True)
    Gene_dot_refGene = models.CharField(
        max_length=25, null=True, db_index=True)
    ExonicFunc_dot_refGene = models.CharField(
        max_length=25, null=True, db_index=True)
    Func_dot_knownGene = models.CharField(
        max_length=25, null=True, db_index=True)
    Gene_dot_knownGene = models.CharField(
        max_length=25, null=True, db_index=True)
    ExonicFunc_dot_knownGene = models.CharField(
        max_length=25, null=True, db_index=True)
    CLNDN = models.CharField(max_length=25, null=True, db_index=True)
    CLNSIG = models.CharField(max_length=25, null=True, db_index=True)
    Polyphen2_HDIV_pred = models.CharField(
        max_length=25, null=True, db_index=True)
    Polyphen2_HVAR_pred = models.CharField(
        max_length=25, null=True, db_index=True)
    SIFT_pred = models.CharField(max_length=25, null=True, db_index=True)
