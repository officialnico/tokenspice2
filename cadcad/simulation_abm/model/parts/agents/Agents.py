import logging
log = logging.getLogger('agents')

import enforce
import math

from BaseAgent import BaseAgent   
from ..util.constants import S_PER_MONTH, S_PER_YEAR

@enforce.runtime_validation
class RouterAgent(BaseAgent):
    def __init__(self, name: str, USD: float, OCEAN: float,
                 receiving_agents : dict):
        """receiving_agents -- [agent_n_name] : method_for_%_going_to_agent_n
        The dict values are methods, not floats, so that the return value
        can change over time. E.g. percent_burn changes.
        """
        super().__init__(name, USD, OCEAN)
        self._receiving_agents = receiving_agents

        #track amounts over time
        self._USD_per_tick = [] #the next tick will record what's in self
        self._OCEAN_per_tick = [] # ""
        
    def takeStep(self, state) -> None:
        #record what we had up until this point
        self._USD_per_tick.append(self.USD())
        self._OCEAN_per_tick.append(self.OCEAN())
        
        #disburse it all, as soon as agent has it
        if self.USD() > 0:
            self._disburseUSD(state)
        if self.OCEAN() > 0:
            self._disburseOCEAN(state)

    def _disburseUSD(self, state) -> None:
        USD = self.USD()
        for name, computePercent in self._receiving_agents.items():
            self._transferUSD(state.getAgent(name), computePercent() * USD)

    def _disburseOCEAN(self, state) -> None:
        OCEAN = self.OCEAN()
        for name, computePercent in self._receiving_agents.items():
            self._transferOCEAN(state.getAgent(name), computePercent() * OCEAN)

    def monthlyUSDreceived(self, state) -> float:
        """Amount of USD received in the past month. 
        Assumes that it disburses USD as soon as it gets it."""
        tick1 = self._tickOneMonthAgo(state)
        tick2 = state.tick
        return float(sum(self._USD_per_tick[tick1:tick2+1]))
    
    def monthlyOCEANreceived(self, state) -> float:
        """Amount of OCEAN received in the past month. 
        Assumes that it disburses OCEAN as soon as it gets it."""
        tick1 = self._tickOneMonthAgo(state)
        tick2 = state.tick
        return float(sum(self._OCEAN_per_tick[tick1:tick2+1]))

    def _tickOneMonthAgo(self, state) -> int:
        t2 = state.tick * state.ss.time_step
        t1 = t2 - S_PER_MONTH
        if t1 < 0:
            return 0
        tick1 = int(max(0, math.floor(t1 / float(state.ss.time_step))))
        return tick1

@enforce.runtime_validation
class OCEANBurnerAgent(BaseAgent):
    def takeStep(self, state):
        if self.USD() > 0:
            #OCEAN price will go up as we buy. Reflect it here.
            nloops = 10
            spend_per_loop = self.USD() / float(nloops)
            for i in range(nloops):
                price = state.OCEANprice() #a func of supply
                OCEAN = spend_per_loop / price
                state._total_OCEAN_burned += OCEAN
                state._total_OCEAN_burned_USD += spend_per_loop
            self._wallet._USD = 0.0 #we've spent the USD!
                    
@enforce.runtime_validation
class GrantGivingAgent(BaseAgent):
    """
    Disburses funds at a fixed # evenly-spaced intervals.
    Same amount each time.
    """
    def __init__(self, name: str, USD: float, OCEAN: float,
                 receiving_agent_name: str,
                 s_between_grants: int,  n_actions: int):
        super().__init__(name, USD, OCEAN)
        self._receiving_agent_name: str = receiving_agent_name
        self._s_between_grants: int = s_between_grants
        self._USD_per_grant: float = USD / float(n_actions)
        self._OCEAN_per_grant: float = OCEAN / float(n_actions)
        
        self._tick_last_disburse = None
        
    def takeStep(self, state):
        do_disburse = False
        if self._tick_last_disburse is None:
            do_disburse = True
        else:
            n_ticks_since = state.tick - self._tick_last_disburse
            n_s_since = n_ticks_since * state.ss.time_step
            n_s_thr = self._s_between_grants            
            do_disburse = (n_s_since >= n_s_thr)
        
        if do_disburse:
            self._disburseFunds(state)
            self._tick_last_disburse = state.tick

    def _disburseFunds(self, state):
        #same amount each time
        receiving_agent = state.getAgent(self._receiving_agent_name)
        
        USD = min(self.USD(), self._USD_per_grant)
        self._transferUSD(receiving_agent, USD)
                
        OCEAN = min(self.OCEAN(), self._OCEAN_per_grant)
        self._transferOCEAN(receiving_agent, OCEAN)
        
@enforce.runtime_validation
class GrantTakingAgent(BaseAgent):    
    def __init__(self, name: str, USD: float, OCEAN: float):
        super().__init__(name, USD, OCEAN)
        self._spent_at_tick = 0.0 #USD and OCEAN (in USD) spent
        
    def takeStep(self, state):
        self._spent_at_tick = self.USD() + self.OCEAN() * state.OCEANprice()
        
        #spend it all, as soon as agent has it
        self._transferUSD(None, self.USD())
        self._transferOCEAN(None, self.OCEAN())

    def spentAtTick(self) -> float:
        return self._spent_at_tick

@enforce.runtime_validation
class MarketplacesAgent(BaseAgent):
    def __init__(self,
                 name: str, USD: float, OCEAN: float,
                 toll_agent_name: str,
                 n_marketplaces: float,
                 revenue_per_marketplace_per_s: float,
                 time_step: int,
                 ):
        super().__init__(name, USD, OCEAN)
        self._toll_agent_name: str = toll_agent_name

        #set initial values. These grow over time.
        self._n_marketplaces: float = n_marketplaces
        self._revenue_per_marketplace_per_s: float = revenue_per_marketplace_per_s
        self._time_step: int = time_step

    def numMarketplaces(self) -> float:
        return self._n_marketplaces
        
    def revenuePerMarketplacePerSecond(self) -> float:
        return self._revenue_per_marketplace_per_s
        
    def takeStep(self, state):
        ratio = state.kpis.mktsRNDToSalesRatio()
        mkts_growth_rate_per_year = state.ss.annualMktsGrowthRate(ratio)
        mkts_growth_rate_per_tick = self._growthRatePerTick(mkts_growth_rate_per_year)
        
        #*grow* the number of marketplaces, and revenue per marketplace
        self._n_marketplaces *= (1.0 + mkts_growth_rate_per_tick)
        self._revenue_per_marketplace_per_s *= (1.0 + mkts_growth_rate_per_tick)

        #compute sales -> toll -> send funds accordingly
        #NOTE: we don't bother modeling marketplace profits or tracking mkt wallet $
        sales = self._salesPerTick()
        toll = sales * state.marketplacePercentTollToOcean()
        toll_agent = state.getAgent(self._toll_agent_name)
        toll_agent.receiveUSD(toll)

    def _salesPerTick(self) -> float:
        return self._n_marketplaces * self._revenue_per_marketplace_per_s \
            * self._time_step

    def _growthRatePerTick(self, g_per_year: float) -> float:
        """
        @arguments 
          g_per_year -- growth rate per year, e.g. 0.05 for 5% annual rate
        """
        ticks_per_year = S_PER_YEAR / float(self._time_step)
        g_per_tick = math.pow(g_per_year + 1, 1.0/ticks_per_year) - 1.0
        return g_per_tick

        
import random
import uuid
from enum import Enum
from os.path import abspath
from typing import List, Tuple

import numpy as np

import config
from convictionvoting import trigger_threshold
from hatch import TokenBatch
from utils import probability, attrs


ProposalStatus = Enum("ProposalStatus", "CANDIDATE ACTIVE COMPLETED FAILED")
# candidate: proposal is being evaluated by the commons
# active: has been approved and is funded
# completed: the proposal was effective/successful
# failed: did not get to active status or failed after funding


class Proposal:
    def __init__(self, funds_requested: int, trigger: float):
        self.conviction = 0
        self.status = ProposalStatus.CANDIDATE
        self.age = 0
        self.funds_requested = funds_requested
        self.trigger = trigger

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, attrs(self))

    def update_age(self):
        self.age += 1
        return self.age

    def update_threshold(self, funding_pool: float, token_supply: float, max_proposal_request: float):
        if self.status == ProposalStatus.CANDIDATE:
            self.trigger = trigger_threshold(
                self.funds_requested, funding_pool, token_supply, max_proposal_request)
        else:
            self.trigger = np.nan
        return self.trigger

    def has_enough_conviction(self, funding_pool: float, token_supply: float, max_proposal_request):
        """
        It's just a conviction < threshold check, but we recalculate the
        trigger_threshold so that the programmer doesn't have to remember to run
        update_threshold before running this method.
        """
        if self.status == ProposalStatus.CANDIDATE:
            threshold = trigger_threshold(
                self.funds_requested, funding_pool, token_supply, max_proposal_request)
            if self.conviction < threshold:
                return False
            return True
        else:
            raise(Exception(
                "Proposal is not a Candidate Proposal and so asking it if it will pass is inappropriate"))


class Participant:
    def __init__(self, holdings: TokenBatch):
        self.sentiment = np.random.rand()
        self.holdings = holdings

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, attrs(self))

    def buy(self) -> float:
        """
        If the Participant decides to buy more tokens, returns the number of
        tokens. Otherwise, return 0.

        This method does not modify itself, it simply returns the answer so that
        cadCAD's state update functions will make the changes and maintain its
        functional-ness.
        """
        engagement_rate = 0.3 * self.sentiment
        force = self.sentiment - config.sentiment_sensitivity
        if probability(engagement_rate) and force > 0:
            delta_holdings = np.random.rand() * force * config.delta_holdings_scale
            return delta_holdings
        return 0

    def sell(self) -> float:
        """
        Decides to sell some tokens, and if so how many. If the Participant
        decides to sell some tokens, returns the number of tokens. Otherwise,
        return 0.

        This method does not modify itself, it simply returns the answer so that
        cadCAD's state update functions will make the changes and maintain its
        functional-ness.
        """
        engagement_rate = 0.3 * self.sentiment
        force = self.sentiment - config.sentiment_sensitivity
        if probability(engagement_rate) and force < 0:
            delta_holdings = np.random.rand() * force * self.holdings.spendable()
            return delta_holdings
        return 0

    def increase_holdings(self, x: float):
        """
        increase_holdings() is the opposite of spend() and adds to the
        nonvesting part of the TokenBatch.
        """
        self.holdings.nonvesting += x
        return self.holdings.vesting, self.holdings.vesting_spent, self.holdings.nonvesting

    def spend(self, x: float) -> Tuple[float, float, float]:
        """
        Participant.spend() is simply a front to TokenBatch.spend().
        """
        return self.holdings.spend(x)

    def create_proposal(self, total_funds_requested, median_affinity, funding_pool) -> bool:
        """
        Here the Participant will decide whether or not to create a new
        Proposal.

        This equation, originally from randomly_gen_new_proposal(), is a
        systems-type simulation. An individual Participant would likely think in
        a different way, and thus this equation should change. Nevertheless for
        simplicity's sake, we use this same equation for now.

        Explanation: If the median affinity is high, the Proposal Rate should be
        high.

        If total funds_requested in candidate proposals is much lower than the
        funding pool (i.e. the Commons has lots of spare money), then people are
        just going to pour in more Proposals.
        """
        percent_of_funding_pool_being_requested = total_funds_requested/funding_pool
        proposal_rate = median_affinity / \
            (1 + percent_of_funding_pool_being_requested)
        new_proposal = probability(proposal_rate)
        return new_proposal

    def vote_on_candidate_proposals(self, candidate_proposals: dict) -> dict:
        """
        Here the Participant decides which Candidate Proposals he will stake
        tokens on. This method does not decide how many tokens he will stake
        on them, because another function should decide how the tokens should be
        balanced across the newly supported proposals and the ones the
        Participant already supported.

        Copied from
        participants_buy_more_if_they_feel_good_and_vote_for_proposals()

        candidate dict format:
        {
            proposal_idx: affinity,
            ...
        }

        NOTE: the original cadCAD policy returned {'delta_holdings':
        delta_holdings, 'proposals_supported': proposals_supported}
        proposals_supported seems to include proposals ALREADY supported by the
        participant, but I don't think it is needed.
        """
        new_voted_proposals = {}
        engagement_rate = 1.0
        if probability(engagement_rate):
            # Put your tokens on your favourite Proposals, where favourite is
            # calculated as 0.75 * (the affinity for the Proposal you like the
            # most) e.g. if there are 2 Proposals that you have affinity 0.8,
            # 0.9, then 0.75*0.9 = 0.675, so you will end up voting for both of
            # these Proposals
            #
            # A Zargham work of art.
            for candidate in candidate_proposals:
                affinity = candidate_proposals[candidate]
                # Hardcoded 0.75 instead of a configurable sentiment_sensitivity
                # because modifying sentiment_sensitivity without changing the
                # hardcoded cutoff value of 0.5 may cause unintended behaviour.
                # Also, 0.75 is a reasonable number in this case.
                cutoff = 0.75 * np.max(list(candidate_proposals.values()))
                if cutoff < .5:
                    cutoff = .5

                if affinity > cutoff:
                    new_voted_proposals[candidate] = affinity

        return new_voted_proposals

    def stake_across_all_supported_proposals(self, supported_proposals: List[Tuple[float, int]]) -> dict:
        """
        Rebalances the Participant's tokens across the (possibly updated) list of Proposals
        supported by this Participant.

        These tokens can come from a Participant's vesting and nonvesting TokenBatches.

        supported_proposals format:
        [(affinity, proposal_idx)...]
        """
        tokens_per_supported_proposal = {}
        supported_proposals = sorted(
            supported_proposals, key=lambda tup: tup[0])

        affinity_total = sum([a for a, idx in supported_proposals])
        for affinity, proposal_idx in supported_proposals:
            tokens_per_supported_proposal[proposal_idx] = self.holdings.total * (
                affinity/affinity_total)

        return tokens_per_supported_proposal

    def wants_to_exit(self):
        """
        Returns True if the Participant wants to exit (if sentiment < 0.5,
        random chance of exiting), otherwise False
        """
        if self.sentiment < 0.5:
            engagement_rate = 0.3 * self.sentiment
            return probability(1-engagement_rate)
        return False

