# Program Logic

import requests
import json

uniV3Endpoint = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

# This function will request data from the desired API (in this case we are using Uniswap V3 subgraph endpoint
def retrieve_uniswap_info():

    query = """ 
        {
            pools(orderBy: totalValueLockedETH, orderDirection: desc, first: 1000) {
                id
                totalValueLockedETH
                token0Price
                token1Price
                feeTier
                token0 {
                  id
                  symbol
                  name
                  decimals
                }
                token1 {
                  id
                  symbol
                  name
                  decimals
                }
            }
        } 
    """

    req = requests.post(uniV3Endpoint, json={'query': query})
    json_dict = json.loads(req.text)

    return json_dict

# This function will structure the list of pairs by building the triage of pairs
def structure_triangular_pairs(pools):

    print("Structuring list")

    remove_duplicate_list = []
    triangular_pairs_list = []

    # Pair A
    for pairA in pools:

        pairA_base = pairA["token0"]["symbol"]
        pairA_quote = pairA["token1"]["symbol"]

        a_token0_id = pairA["token0"]["id"]
        a_token0_price = pairA["token0Price"]
        a_token0_decimals = pairA["token0"]["decimals"]

        a_token1_id = pairA["token1"]["id"]
        a_token1_price = pairA["token1Price"]
        a_token1_decimals = pairA["token1"]["decimals"]

        aContract = pairA["id"]
        aPairBox = [pairA_base, pairA_quote]
        contractsBox = [a_token0_id, a_token1_id]
        aPair = pairA_base + "_" + pairA_quote

        # Pair B
        for pairB in pools:

            pairB_base = pairB["token0"]["symbol"]
            pairB_quote = pairB["token1"]["symbol"]

            b_token0_id = pairB["token0"]["id"]
            b_token0_price = pairB["token0Price"]
            b_token0_decimals = pairB["token0"]["decimals"]

            b_token1_id = pairB["token1"]["id"]
            b_token1_price = pairB["token1Price"]
            b_token1_decimals = pairB["token1"]["decimals"]

            bContract = pairB["id"]

            bPair = pairB_base + "_" + pairB_quote

            if aPair != bPair:

                if (pairB_base in aPairBox or pairB_quote in aPairBox) and (b_token0_id in contractsBox or b_token1_id in contractsBox):

                    # Pair C
                    for pairC in pools:

                        pairC_base = pairC["token0"]["symbol"]
                        pairC_quote = pairC["token1"]["symbol"]

                        c_token0_id = pairC["token0"]["id"]
                        c_token0_price = pairC["token0Price"]
                        c_token0_decimals = pairC["token0"]["decimals"]

                        c_token1_id = pairC["token1"]["id"]
                        c_token1_price = pairC["token1Price"]
                        c_token1_decimals = pairC["token1"]["decimals"]

                        cContract = pairC["id"]

                        cPair = pairC_base + "_" + pairC_quote

                        if cPair != aPair and cPair != bPair:

                            pair_box = [pairA_base, pairA_quote, pairB_base, pairB_quote, pairC_base, pairC_quote]
                            contractsBox = [a_token0_id, a_token1_id, b_token0_id, b_token1_id, c_token0_id, c_token1_id]

                            counts_pairC_quote = 0

                            for i in pair_box:
                                if i == pairC_quote:
                                    counts_pairC_quote += 1

                            counts_c_token1_id = 0

                            for i in contractsBox:
                                if i == c_token1_id:
                                    counts_c_token1_id += 1

                            counts_pairC_base = 0

                            for i in pair_box:
                                if i == pairC_base:
                                    counts_pairC_base += 1

                            counts_c_token0_id = 0

                            for i in contractsBox:
                                if i == c_token0_id:
                                    counts_c_token0_id += 1

                            if counts_pairC_base == 2 and counts_pairC_quote == 2 and counts_c_token0_id == 2 and counts_c_token1_id == 2 and pairC_base != pairC_quote:

                                combined = aPair + "," + bPair + "," + cPair
                                unique_item = ''.join(sorted(combined))

                                if unique_item not in remove_duplicate_list:

                                    match_dict = {
                                        "pairA_base": pairA_base,
                                        "pairB_base": pairB_base,
                                        "pairC_base": pairC_base,
                                        "pairA_quote": pairA_quote,
                                        "pairB_quote": pairB_quote,
                                        "pairC_quote": pairC_quote,
                                        "a_token0_id": a_token0_id,
                                        "b_token0_id": b_token0_id,
                                        "c_token0_id": c_token0_id,
                                        "a_token1_id": a_token1_id,
                                        "b_token1_id": b_token1_id,
                                        "c_token1_id": c_token1_id,
                                        "a_token0_price": a_token0_price,
                                        "b_token0_price": b_token0_price,
                                        "c_token0_price": c_token0_price,
                                        "a_token1_price": a_token1_price,
                                        "b_token1_price": b_token1_price,
                                        "c_token1_price": c_token1_price,
                                        "a_token0_decimals": a_token0_decimals,
                                        "b_token0_decimals": b_token0_decimals,
                                        "c_token0_decimals": c_token0_decimals,
                                        "a_token1_decimals": a_token1_decimals,
                                        "b_token1_decimals": b_token1_decimals,
                                        "c_token1_decimals": c_token1_decimals,
                                        "aContract": aContract,
                                        "bContract": bContract,
                                        "cContract": cContract,
                                        "pairA": aPair,
                                        "pairB": bPair,
                                        "pairC": cPair,
                                        "combined": combined
                                    }

                                    remove_duplicate_list.append(unique_item)
                                    triangular_pairs_list.append(match_dict)

                                    print("Saving:", combined)

    with open("structured_triangular_pairs.json", "w") as fp:
        json.dump(triangular_pairs_list, fp)

    return len(triangular_pairs_list)

# This function will calculate surface arb potential
def triangular_arb_surface_rate(min_rate):

    with open("structured_triangular_pairs.json") as json_file:
        structured_triangular_pairs = json.load(json_file)

    surface_rate_list = []

    for triangular_pair in structured_triangular_pairs:

        min_surface_rate = min_rate
        surface_dict = {}
        pool_contract_2 = ""
        pool_contract_3 = ""
        pool_direction_trade_1 = ""
        pool_direction_trade_2 = ""
        pool_direction_trade_3 = ""

        direction_list = ["forward", "reverse"]

        for direction in direction_list:

            pairA_base = triangular_pair["pairA_base"]
            pairA_quote = triangular_pair["pairA_quote"]
            pairB_base = triangular_pair["pairB_base"]
            pairB_quote = triangular_pair["pairB_quote"]
            pairC_base = triangular_pair["pairC_base"]
            pairC_quote = triangular_pair["pairC_quote"]

            a_token0_price = float(triangular_pair["a_token0_price"])
            a_token1_price = float(triangular_pair["a_token1_price"])
            b_token0_price = float(triangular_pair["b_token0_price"])
            b_token1_price = float(triangular_pair["b_token1_price"])
            c_token0_price = float(triangular_pair["c_token0_price"])
            c_token1_price = float(triangular_pair["c_token1_price"])

            aContract = triangular_pair["aContract"]
            bContract = triangular_pair["bContract"]
            cContract = triangular_pair["cContract"]

            starting_amount = 1
            acquired_coin_t2 = 0
            acquired_coin_t3 = 0
            calculated = 0

            swap_1 = 0
            swap_2 = 0
            swap_3 = 0
            swap_1_rate = 0
            swap_2_rate = 0
            swap_3_rate = 0

            # Assume start with base of "A" pair if forward
            if direction == "forward":
                swap_1 = pairA_base
                swap_2 = pairA_quote
                swap_1_rate = a_token1_price
                pool_direction_trade_1 = "baseToQuote"

            # Assume start with quote of "A" pair if reverse
            if direction == "reverse":
                swap_1 = pairA_quote
                swap_2 = pairA_base
                swap_1_rate = a_token0_price
                pool_direction_trade_1 = "quoteToBase"

            pool_contract_1 = aContract
            acquired_coin_t1 = starting_amount * swap_1_rate

            if direction == "forward":

                if pairA_quote == pairB_quote and calculated == 0:

                    swap_2_rate = b_token0_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "quoteToBase"
                    pool_contract_2 = bContract

                    if pairB_base == pairC_base:
                        swap_3 = pairC_base
                        swap_3_rate = c_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = cContract

                    if pairB_base == pairC_quote:
                        swap_3 = pairC_quote
                        swap_3_rate = c_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = cContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            if direction == "forward":

                if pairA_quote == pairB_quote and calculated == 0:

                    swap_2_rate = b_token1_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "baseToQuote"
                    pool_contract_2 = bContract

                    if pairB_quote == pairC_base:
                        swap_3 = pairC_base
                        swap_3_rate = c_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = cContract

                    if pairB_quote == pairC_quote:
                        swap_3 = pairC_quote
                        swap_3_rate = c_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = cContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            if direction == "forward":

                if pairA_quote == pairC_quote and calculated == 0:

                    swap_2_rate = c_token0_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "quoteToBase"
                    pool_contract_2 = cContract

                    if pairC_base == pairB_base:
                        swap_3 = pairB_base
                        swap_3_rate = b_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = bContract

                    if pairC_base == pairB_quote:
                        swap_3 = pairB_quote
                        swap_3_rate = b_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = bContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            if direction == "forward":

                if pairA_quote == pairC_base and calculated == 0:

                    swap_2_rate = c_token1_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "baseToQuote"
                    pool_contract_2 = cContract

                    if pairC_quote == pairB_base:
                        swap_3 = pairB_base
                        swap_3_rate = b_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = bContract

                    if pairC_quote == pairB_quote:
                        swap_3 = pairB_quote
                        swap_3_rate = b_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = bContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            if direction == "reverse":

                if pairA_base == pairB_base and calculated == 0:

                    swap_2_rate = b_token1_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "baseToQuote"
                    pool_contract_2 = bContract

                    if pairB_quote == pairC_quote:
                        swap_3 = pairC_quote
                        swap_3_rate = c_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = cContract

                    if pairB_quote == pairC_base:
                        swap_3 = pairC_base
                        swap_3_rate = c_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = cContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            if direction == "reverse":

                if pairA_base == pairB_quote and calculated == 0:

                    swap_2_rate = b_token0_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "quoteToBase"
                    pool_contract_2 = bContract

                    if pairB_base == pairC_quote:
                        swap_3 = pairC_quote
                        swap_3_rate = c_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = cContract

                    if pairB_base == pairC_base:
                        swap_3 = pairC_base
                        swap_3_rate = c_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = cContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            if direction == "reverse":

                if pairA_base == pairC_base and calculated == 0:

                    swap_2_rate = c_token1_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "baseToQuote"
                    pool_contract_2 = cContract

                    if pairC_quote == pairB_quote:
                        swap_3 = pairB_quote
                        swap_3_rate = b_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = bContract

                    if pairC_quote == pairB_base:
                        swap_3 = pairB_base
                        swap_3_rate = b_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = bContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            if direction == "reverse":

                if pairA_base == pairC_quote and calculated == 0:

                    swap_2_rate = c_token0_price
                    acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                    pool_direction_trade_2 = "quoteToBase"
                    pool_contract_2 = cContract

                    if pairC_base == pairB_quote:
                        swap_3 = pairB_quote
                        swap_3_rate = b_token0_price
                        pool_direction_trade_3 = "quoteToBase"
                        pool_contract_3 = bContract

                    if pairC_base == pairB_base:
                        swap_3 = pairB_base
                        swap_3_rate = b_token1_price
                        pool_direction_trade_3 = "baseToQuote"
                        pool_contract_3 = bContract

                    acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                    calculated = 1

            profit_loss = acquired_coin_t3 - starting_amount
            profit_loss_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

            trade_description_1 = f"Start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}."
            trade_description_2 = f"Swap {acquired_coin_t1} of {swap_2} at {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}."
            trade_description_3 = f"Swap {acquired_coin_t2} of {swap_3} at {swap_3_rate} for {swap_1} acquiring {acquired_coin_t3}."

            if profit_loss_perc >= min_surface_rate:

                surface_dict = {
                    "swap1": swap_1,
                    "swap2": swap_2,
                    "swap3": swap_3,
                    "poolContract1": pool_contract_1,
                    "poolContract2": pool_contract_2,
                    "poolContract3": pool_contract_3,
                    "poolDirectionTrade1": pool_direction_trade_1,
                    "poolDirectionTrade2": pool_direction_trade_2,
                    "poolDirectionTrade3": pool_direction_trade_3,
                    "startingAmount": starting_amount,
                    "acquiredCoinT1": acquired_coin_t1,
                    "acquiredCoinT2": acquired_coin_t2,
                    "acquiredCoinT3": acquired_coin_t3,
                    "swap1Rate": swap_1_rate,
                    "swap2Rate": swap_2_rate,
                    "swap3Rate": swap_3_rate,
                    "profitLoss": profit_loss,
                    "profitLossPerc": profit_loss_perc,
                    "direction": direction,
                    "tradeDesc1": trade_description_1,
                    "tradeDesc2": trade_description_2,
                    "tradeDesc3": trade_description_3
                }

                surface_rate_list.append(surface_dict)

    with open("uniswap_surface_rates.json", "w") as fp:
        json.dump(surface_rate_list, fp)

    return len(surface_rate_list)
