import math
from typing import List, Dict, Tuple, Optional, Any, Union

class FundAllocator:
    """Handles fund allocation based on proportional contributions and priorities"""
    
    def __init__(self, platform_fee_percent: float = 0.05, payment_processing_fee_percent: float = 0.03):
        """
        Initialize the fund allocator with fee rates
        
        Args:
            platform_fee_percent: Platform fee as a decimal (0.05 = 5%)
            payment_processing_fee_percent: Payment processing fee as a decimal (0.03 = 3%)
        """
        self.platform_fee_percent = platform_fee_percent
        self.payment_processing_fee_percent = payment_processing_fee_percent
        self.exchange_rate_buffer = 0.05  # 5% buffer for exchange rate fluctuations
    
    def calculate_total_required(self, gift_price: float) -> Dict[str, float]:
        """
        Calculate the total amount required including fees
        
        Args:
            gift_price: The price of the gift
            
        Returns:
            Dictionary with breakdown of required funds
        """
        platform_fee = gift_price * self.platform_fee_percent
        payment_fee = gift_price * self.payment_processing_fee_percent
        buffer = gift_price * self.exchange_rate_buffer
        
        total_required = gift_price + platform_fee + payment_fee + buffer
        
        return {
            "gift_price": gift_price,
            "platform_fee": platform_fee,
            "payment_processing_fee": payment_fee,
            "exchange_buffer": buffer,
            "total_required": total_required
        }
    
    def allocate_individual_contributions(self, 
                                         contributors: List[Dict[str, Any]], 
                                         gift_price: float) -> List[Dict[str, Any]]:
        """
        Allocate individual contributions proportionally
        
        Args:
            contributors: List of contributor dictionaries with 'user_id' and 'amount' keys
            gift_price: The price of the gift
            
        Returns:
            Contributors with added individual shares
        """
        total_collected = sum(c['amount'] for c in contributors)
        
        # Calculate each contributor's proportional share
        for contributor in contributors:
            proportion = contributor['amount'] / total_collected
            contributor['individual_share'] = proportion * gift_price
            contributor['percentage'] = proportion * 100
            
        return contributors
    
    def handle_overfunding(self, 
                          total_collected: float, 
                          target_amount: float,
                          contributors: List[Dict[str, Any]],
                          option: str = 'proportional_refund') -> Dict[str, Any]:
        """
        Handle cases where more money is collected than needed
        
        Args:
            total_collected: Total amount collected
            target_amount: Target amount needed for the gift
            contributors: List of contributors with their contributions
            option: Strategy for handling surplus ('proportional_refund', 'keep', 'bonus_tier')
            
        Returns:
            Dictionary with allocation details
        """
        surplus = total_collected - target_amount
        
        result = {
            'total_collected': total_collected,
            'target_amount': target_amount,
            'surplus': surplus,
            'option': option,
            'contributors': []
        }
        
        if option == 'proportional_refund':
            # Refund surplus proportionally to contributors
            for contributor in contributors:
                proportion = contributor['amount'] / total_collected
                refund_amount = surplus * proportion
                contributor['refund'] = refund_amount
                contributor['final_contribution'] = contributor['amount'] - refund_amount
                result['contributors'].append(contributor)
                
        elif option == 'keep':
            # Let receiver keep surplus (just pass through contributions)
            for contributor in contributors:
                contributor['refund'] = 0
                contributor['final_contribution'] = contributor['amount']
                result['contributors'].append(contributor)
                
        elif option == 'bonus_tier':
            # Allocate surplus to bonus gift (this would use LLM in practice)
            result['bonus_gift_budget'] = surplus
            
            # Just pass through contributions
            for contributor in contributors:
                contributor['refund'] = 0
                contributor['final_contribution'] = contributor['amount']
                result['contributors'].append(contributor)
        
        return result
    
    def handle_underfunding(self, 
                           total_collected: float, 
                           target_amount: float,
                           contributors: List[Dict[str, Any]],
                           item_info: Dict[str, Any] = None,
                           option: str = 'partial_fulfillment') -> Dict[str, Any]:
        """
        Handle cases where less money is collected than needed
        
        Args:
            total_collected: Total amount collected
            target_amount: Target amount needed for the gift
            contributors: List of contributors with their contributions
            item_info: Information about the item being purchased
            option: Strategy for handling shortfall ('refund', 'partial', 'extension')
            
        Returns:
            Dictionary with allocation decision
        """
        shortfall = target_amount - total_collected
        
        result = {
            'total_collected': total_collected,
            'target_amount': target_amount,
            'shortfall': shortfall,
            'option': option,
            'contributors': contributors
        }
        
        if option == 'refund':
            # Full refund to all contributors
            for contributor in contributors:
                contributor['refund'] = contributor['amount']
                contributor['final_contribution'] = 0
            
            result['purchase_decision'] = 'refund_all'
            
        elif option == 'partial_fulfillment':
            # Buy what's possible with the funds available
            for contributor in contributors:
                contributor['refund'] = 0
                contributor['final_contribution'] = contributor['amount']
            
            # This would use LLM price matching in practice
            if item_info and 'alternatives' in item_info:
                affordable_alternatives = [
                    alt for alt in item_info['alternatives'] 
                    if alt['price'] <= total_collected
                ]
                
                if affordable_alternatives:
                    best_alternative = max(affordable_alternatives, key=lambda x: x['price'])
                    result['alternative_purchase'] = best_alternative
                    result['purchase_decision'] = 'buy_alternative'
                    result['savings'] = total_collected - best_alternative['price']
                else:
                    # Convert to gift card if no affordable alternatives
                    result['purchase_decision'] = 'gift_card'
            else:
                # Default to gift card if no alternatives available
                result['purchase_decision'] = 'gift_card'
                
        elif option == 'extension':
            # Extend deadline to collect more funds
            for contributor in contributors:
                contributor['refund'] = 0
                contributor['final_contribution'] = contributor['amount']
                
            result['purchase_decision'] = 'extend_deadline'
            result['needed_additional'] = shortfall
            
        return result
    
    def handle_price_changes(self,
                            original_price: float,
                            current_price: float,
                            total_collected: float,
                            contributors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle price changes during a campaign
        
        Args:
            original_price: Original locked price
            current_price: Current price of the item
            total_collected: Total amount collected
            contributors: List of contributors with their contributions
            
        Returns:
            Strategy for handling the price change
        """
        result = {
            'original_price': original_price,
            'current_price': current_price,
            'price_difference': original_price - current_price,
            'total_collected': total_collected,
            'contributors': contributors
        }
        
        if current_price < original_price:
            # Price decreased
            surplus = original_price - current_price
            result['surplus'] = surplus
            
            if surplus / original_price > 0.2:  # Over 20% price drop
                # Suggest using the surplus for upgrades
                result['recommendation'] = 'upgrade'
                result['upgrade_budget'] = surplus
            elif surplus / original_price > 0.05:  # 5-20% price drop
                # Suggest complementary item
                result['recommendation'] = 'complementary_item'
                result['complementary_budget'] = surplus
            else:  # Small price drop
                # Suggest refund
                result['recommendation'] = 'small_refund'
                result['refund_amount'] = surplus
                
        elif current_price > original_price:
            # Price increased
            shortfall = current_price - original_price
            result['shortfall'] = shortfall
            
            if total_collected >= current_price:
                # We have enough funds despite price increase
                result['recommendation'] = 'auto_adjust'
                result['new_target'] = current_price
            else:
                # Need more funds
                result['recommendation'] = 'request_topup'
                result['additional_needed'] = shortfall
                
        else:
            # No price change
            result['recommendation'] = 'no_change'
            
        return result
    
    def prioritize_multi_item_purchase(self,
                                      gift_list: List[Dict[str, Any]],
                                      total_raised: float,
                                      event_date: str) -> List[Dict[str, Any]]:
        """
        Prioritize which items to purchase when there are multiple items
        
        Args:
            gift_list: List of gift items with prices and priorities
            total_raised: Total amount raised
            event_date: Date of the event (for urgency calculation)
            
        Returns:
            Prioritized list of gifts with purchase decisions
        """
        # Sort by priority and affordability
        prioritized_gifts = sorted(
            gift_list,
            key=lambda g: (
                # Priority values should be numeric (3=high, 2=medium, 1=low)
                g.get('priority_value', 2),
                # Favor affordable items
                1 if g['price'] <= total_raised else 0,
                # Favor items that use most of the budget without going over
                g['price'] / total_raised if g['price'] <= total_raised else 0
            ),
            reverse=True  # Highest priority first
        )
        
        # Mark which items we can afford
        remaining_budget = total_raised
        for gift in prioritized_gifts:
            if remaining_budget >= gift['price']:
                gift['can_purchase'] = True
                gift['purchase_decision'] = 'buy'
                remaining_budget -= gift['price']
            else:
                gift['can_purchase'] = False
                
                # Check if we're close to affording it
                if gift['price'] - remaining_budget <= gift['price'] * 0.15:  # Within 15%
                    gift['purchase_decision'] = 'suggest_topup'
                    gift['additional_needed'] = gift['price'] - remaining_budget
                else:
                    gift['purchase_decision'] = 'suggest_alternative'
                    # This would use LLM in practice to find alternatives
                    gift['budget_available'] = remaining_budget
        
        return prioritized_gifts
    
    def handle_fraud_prevention(self, gift_price: float, market_price_sources: List[float]) -> Dict[str, Any]:
        """
        Check if a gift's price is within reasonable market range to prevent fraud
        
        Args:
            gift_price: The listed price of the gift
            market_price_sources: List of prices from different market sources
            
        Returns:
            Fraud assessment
        """
        if not market_price_sources:
            return {
                'assessment': 'unknown',
                'reason': 'No market sources available for comparison'
            }
            
        average_market_price = sum(market_price_sources) / len(market_price_sources)
        max_price = max(market_price_sources)
        min_price = min(market_price_sources)
        
        price_difference_pct = abs(gift_price - average_market_price) / average_market_price
        
        result = {
            'gift_price': gift_price,
            'average_market_price': average_market_price,
            'price_range': {'min': min_price, 'max': max_price},
            'difference_percentage': price_difference_pct * 100
        }
        
        if price_difference_pct > 0.15:  # More than 15% difference
            result['assessment'] = 'potential_fraud'
            if gift_price > average_market_price:
                result['reason'] = 'Price is significantly higher than market average'
            else:
                result['reason'] = 'Price is significantly lower than market average (potential scam or counterfeit)'
        else:
            result['assessment'] = 'reasonable_price'
            result['reason'] = 'Price is within normal market range'
            
        return result 