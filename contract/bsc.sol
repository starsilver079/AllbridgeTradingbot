/**
 * SPDX-License-Identifier: MIT
*/
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface  Iswap {
    function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
}

interface Itrade{
    function buy(uint[] memory amounts, address account, bytes32 to, uint128 lockId, bytes4 destination)external returns(uint256);
    function sell(uint256 lockId, address account, uint256 amount, bytes4 locksource, bytes32 tokensourceaddr, bytes calldata signature) external returns (uint256);
    function convert(address account, uint256 chainId,  uint256 indexfrom, uint256 indexto, uint256 amount) external returns(bool);
}

contract trade is Itrade{
    address USDC = 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56;
    address Swap = 0x10ED43C718714eb63d5aA57B78B54704E256024E;
    address Allbridge = 0xBBbD1BbB4f9b936C3604906D7592A644071dE884;
    address Synapse = 0xd123f70AE324d34A9E76b67a27bf77593bA8749f;
    address token = 0x68784ffaa6Ff05E3e04575DF77960DC1D9F42b4a;
    address[] buypath = [0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56, 0x68784ffaa6Ff05E3e04575DF77960DC1D9F42b4a];
    address[] sellpath = [0x68784ffaa6Ff05E3e04575DF77960DC1D9F42b4a, 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56];
    uint256 public buyresult;
    uint256 public sellresult;
    constructor(){}
    function buy(uint[] memory amounts, address account, bytes32 to, uint128 lockId, bytes4 destination)external override returns(uint256){
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
    function convert(address account, uint256 chainId,uint256 indexfrom, uint256 indexto, uint256 amount) external override returns(bool){
        address btoken = 0x23b891e5C62E0955ae2bD185990103928Ab817b3;
        (bool usdcapprove, ) = USDC.delegatecall(abi.encodeWithSignature("approve(address,uint256)", Synapse, amount));
        require(usdcapprove,"Didn't approve USDC");
        uint256 deadline = block.timestamp + 1000;
        (bool convertsuccess, ) = Synapse.delegatecall(abi.encodeWithSignature("redeemAndSwap(address,uint256,address,uint256,uint8,uint8,uint256,uint256)", account, chainId, btoken, amount, indexfrom, indexto, (amount*997/1000), deadline));
        return convertsuccess;
    } 
}
