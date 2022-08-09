import time
import random
import re
from collections import defaultdict
from logzero import logger

import fuzzy_reasoner.types.Rule


class SolverStats:
    def __init__(self, print_stats_period=1) -> None:
        self.fires = 0
        self.rule_stats = defaultdict(lambda: 0)
        self.pred_stats = defaultdict(lambda: 0)
        self.last_msg = time.time()
        self.solve_start_time = time.time()
        self.print_stats_period = print_stats_period
        self.firings = []
        self.sample_rules = []
        self.collected_rule_samples = []
    
    def rule_fired(self, rule: fuzzy_reasoner.types.Rule):
        """Register Rule firing and optionally print debug info

        Args:
            rule (fuzzy_reasoner.types.Rule.Rule): rule fired
        """

        self.rule_stats[rule.head.predicate.symbol] += 1

        self.check_debug(rule)
    
    def check_debug(self, rule=None):
        """Check if self-debugging is needed and print logs

        Args:
            rule (_type_, optional): rule fired. Defaults to None.
        """
        if self.fires == 0: self.solve_start_time = time.time()
        self.fires += 1
        if (self.fires % 10000 == 0 and 
                time.time() - self.last_msg > self.print_stats_period):

            self.firings = sorted(list(self.rule_stats.items()), 
                                key=lambda x: x[1], reverse=True)[:10]

            self.print_top_firings()
            self.last_msg = time.time()

            if self.firings[0][1] > 100000 and self.firings[1][1] * 50 < self.firings[0][1]:
                logger.warning(f"Rule {self.firings[0][0]} combination explosion detected, started sampling...")
                self.sample_rules.append(self.firings[0][0])
            if time.time() - self.solve_start_time > 30 and len(self.firings) > 3:
                logger.warning(f"Taking too long, sampling of top 3 rules started...")
                self.sample_rules.append(self.firings[0][0])
                self.sample_rules.append(self.firings[1][0])
                self.sample_rules.append(self.firings[2][0])

        
        if self.sample_rules:
            if not random.randint(0, 50):
                for pred_symbol in self.sample_rules:
                    if pred_symbol == rule.head.predicate.symbol:
                        self.collected_rule_samples.append(
                            re.sub(r'\[[0-9-\s\.,e\+]+\]', "[...]", repr(rule).replace("\n", ""))
                        )
            if len(self.collected_rule_samples) >= 10:
                for rsample in self.collected_rule_samples:
                    logger.debug(rsample)
                self.sample_rules.clear()
                self.collected_rule_samples.clear()
                self.rule_stats.clear()
    
    def print_top_firings(self):
        """Print a list of top rules fired
        """

        logger.debug(f"Top firings: {', '.join([f'{rf[0]}:{rf[1]}' for rf in self.firings])}")


