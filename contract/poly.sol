/**
 * SPDX-License-Identifier: MIT
*/
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface  Iswap {
    function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
}

interface Itrade{
    function buy(uint[] memory amounts, address account, bytes32 to, uint128 lockId, bytes4 destination)external returns(uint256) ;
    function sell(uint256 lockId, address account, uint256 amount, bytes4 locksource, bytes32 tokensourceaddr, bytes calldata signature) external returns (uint256);
    function convert(address account, uint256 chainId,  uint256 indexfrom, uint256 indexto, uint256 amount) external returns(bool);
}

contract trade is Itrade{
    address USDC = 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174;
    address Swap = 0xC0788A3aD43d79aa53B09c2EaCc313A787d1d607;
    address Allbridge = 0xBBbD1BbB4f9b936C3604906D7592A644071dE884;
    address Synapse = 0x8F5BBB2BB8c2Ee94639E55d5F41de9b4839C1280;
    address token = 0x04429fbb948BBD09327763214b45e505A5293346;
    address[] buypath = [0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174,0x04429fbb948BBD09327763214b45e505A5293346];
    address[] sellpath = [0x04429fbb948BBD09327763214b45e505A5293346,0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174];
    uint256 public buyresult;
    uint256 public sellresult;

    constructor(){}

    function buy(uint[] memory amounts, address account, bytes32 to, uint128 lockId, bytes4 destination)external override returns(uint256) {
        (bool usdcapprove, ) = USDC.delegatecall(abi.encodeWithSignature("approve(address,uint256)", Swap, amounts[0]));
        uint deadline = block.timestamp + 1000;
        require(usdcapprove,"Didn't approve USDC");
        (bool swapsuccess, ) = Swap.delegatecall(abi.encodeWithSignature("swapExactTokensForTokens(uint256,uint256,address[],address,uint256)", amounts[0], amounts[1], buypath, account, deadline));
        require(swapsuccess, "Didn't swap");
        uint256 amount = IERC20(token).balanceOf(account);
        (bool abrapprove, ) = token.delegatecall(abi.encodeWithSignature("approve(address,uint256)", Allbridge, amount));
        require(abrapprove, "Didn't approve ABR");
        (bool locksuccess, ) = Allbridge.delegatecall(abi.encodeWithSignature("lock(uint128,address,bytes32,bytes4,uint256)", lockId,token,to,destination,amount));
        require(locksuccess,"Didn't lock");
        buyresult = amount;
        return buyresult;
    }
    function sell(uint256 lockId, address account, uint256 amount, bytes4 locksource, bytes32 tokensourceaddr, bytes calldata signature) external override returns (uint256){
        (bool unlocksuccess, ) = Allbridge.delegatecall(abi.encodeWithSignature("unlock(uint128,address,uint256,bytes4,bytes4,bytes32,bytes)", lockId, account, amount, locksource, locksource, tokensourceaddr, signature));
        require(unlocksuccess, "Didn't unlock");
        (bool abrapprove, ) = token.delegatecall(abi.encodeWithSignature("approve(address,uint256)", Swap, amount));
        require(abrapprove, "Didn't approve ABR");
        uint256[] memory amounts = Iswap(Swap).getAmountsOut(amount, sellpath);
        uint deadline = block.timestamp + 1000;
        (bool swapsuccess, ) = Swap.delegatecall(abi.encodeWithSignature("swapExactTokensForTokens(uint256,uint256,address[],address,uint256)", amounts[0], amounts[1], sellpath, account, deadline));
        require(swapsuccess, "Didn't swap");
        sellresult = IERC20(USDC).balanceOf(account);
        return sellresult;
    }
    function convert(address account, uint256 chainId, uint256 indexfrom, uint256 indexto, uint256 amount) external override returns(bool){
        address btoken = 0xB6c473756050dE474286bED418B77Aeac39B02aF;
        (bool usdcapprove, ) = USDC.delegatecall(abi.encodeWithSignature("approve(address,uint256)", Synapse, amount));
        require(usdcapprove,"Didn't approve USDC");
        uint256 deadline = block.timestamp + 1000;
        (bool convertsuccess, ) = Synapse.delegatecall(abi.encodeWithSignature("redeemAndSwap(address,uint256,address,uint256,uint8,uint8,uint256,uint256)", account, chainId, btoken, amount, indexfrom, indexto, (amount*997/1000), deadline));
        return convertsuccess;
    } 
}
