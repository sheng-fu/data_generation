from utils import data_generator
from utils.conjugate import *
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
from utils.vocab_sets import *
from utils.string_utils import string_beautify
import inflect

class PossessGenerator(data_generator.PresuppositionGenerator):
    def __init__(self):
        super().__init__(
            uid="possessed_definites_uniqueness"
        )
        self.safe_nouns = np.intersect1d(np.union1d(np.setdiff1d(all_nouns, all_animate_nouns), all_relational_poss_nouns), all_singular_nouns)
        real_auxs = ["do", "does", "did", "is", "are", "was", "were", "has", "have", "had"]
        m_auxs = ["might", "would", "could", "should", "will", "can"]
        self.real_auxs = reduce(np.union1d, [get_all("expression", s, all_modals_auxs) for s in real_auxs])
        self.m_auxs = reduce(np.union1d, [get_all("expression", s, all_modals_auxs) for s in m_auxs])
        self.rogatives = get_all_conjunctive([("category", "(S\\NP)/Q"), ("finite", "1")])

    def sample(self):
        # John's sister has      left.
        # N1  's N2     aux_real V_real

        # John has  a sister
        # N1   HAVE D N2

        # Bill wonders whether John's sister has      left.
        # N0   V_rog   WHETHER N1  's N2     aux_real V_real

        # John's sister should leave.
        # N1  's N2     aux_m  V_m

        # John's sister has      not left.
        # N1  's N2     aux_real NOT V_real

        N1 = N_to_DP_mutate(choice(get_all("animate", "1", all_nouns)))
        N1_alt = N_to_DP_mutate(choice(get_all("animate", "1", all_nouns), avoid=N1))
        N2 = choice(self.safe_nouns)
        s_poss = "'" if N1["pl"] == "1" and N1[0][-1] == "s" else "'s"
        V = choice(get_matched_by(N2, "arg_1", all_bare_verbs))
        aux_real = choice(get_matched_by(N2, "arg_1", get_matched_by(V, "arg_2", self.real_auxs)))
        V_m = get_bare_form(V)
        aux_m = choice(self.m_auxs)
        v_args = verb_args_from_verb(V, subj=N2, allow_negated=False)
        VP = V_to_VP_mutate(V, aux=False, args=v_args)
        HAVE = "has" if N1["sg"] == "1" else "have"
        V_rog = choice(self.rogatives)
        N0 = N_to_DP_mutate(choice(get_matches_of(V_rog, "arg_1", all_nouns)))


        unembedded_trigger = "%s%s %s %s %s." % (N1[0], s_poss, N2[0], aux_real[0], VP[0])
        negated_trigger = embed_in_negation(unembedded_trigger, neutral=False)
        interrogative_trigger = embed_in_question(unembedded_trigger)
        modal_trigger = embed_in_modal(unembedded_trigger)
        conditional_trigger = embed_in_conditional(unembedded_trigger)

        presupposition = "%s %s exactly one %s." % (N1[0], HAVE, N2[0])
        negated_presupposition = embed_in_negation(presupposition, neutral=True)
        neutral_presupposition = "%s %s exactly one %s." % (N1_alt[0], HAVE, N2[0])

        data = self.build_presupposition_paradigm(unembedded_trigger=unembedded_trigger,
                                                  negated_trigger=negated_trigger,
                                                  interrogative_trigger=interrogative_trigger,
                                                  modal_trigger=modal_trigger,
                                                  conditional_trigger=conditional_trigger,
                                                  presupposition=presupposition,
                                                  negated_presupposition=negated_presupposition,
                                                  neutral_presupposition=neutral_presupposition)
        return data, presupposition

generator = PossessGenerator()
generator.generate_paradigm(number_to_generate=100, rel_output_path="outputs/nli/%s.jsonl" % generator.uid)
