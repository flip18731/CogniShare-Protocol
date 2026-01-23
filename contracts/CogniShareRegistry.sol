// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title CogniShareRegistry
 * @author CogniShare Protocol Team
 * @notice Smart contract for tracking AI knowledge citations with micropayments
 * @dev Implements x402 protocol on Cronos - every citation is recorded on-chain
 * 
 * This contract creates an immutable, auditable record of:
 * - Who paid for knowledge (AI agent wallet)
 * - Who created the knowledge (content author wallet)
 * - What was cited (content hash)
 * - When it happened (block timestamp)
 * - How much was paid (CRO amount)
 * 
 * Hackathon Submission: Cronos EVM
 */
contract CogniShareRegistry {
    
    // =============================================================================
    // Events
    // =============================================================================
    
    /**
     * @notice Emitted when an AI cites knowledge and pays the author
     * @param payer Address of the entity paying (AI agent wallet)
     * @param author Address of the content creator receiving payment
     * @param contentHash Hash of the cited content (for attribution)
     * @param amount Amount of CRO paid in Wei
     * @param timestamp Block timestamp of the citation
     */
    event Citation(
        address indexed payer,
        address indexed author,
        string contentHash,
        uint256 amount,
        uint256 timestamp
    );
    
    /**
     * @notice Emitted when a payment fails (for debugging)
     * @param author Address that was supposed to receive payment
     * @param amount Amount that failed to transfer
     */
    event PaymentFailed(
        address indexed author,
        uint256 amount
    );
    
    // =============================================================================
    // State Variables
    // =============================================================================
    
    /// @notice Total number of citations recorded on-chain
    uint256 public totalCitations;
    
    /// @notice Total CRO distributed to authors (in Wei)
    uint256 public totalPaid;
    
    /// @notice Mapping of author address to total earnings
    mapping(address => uint256) public authorEarnings;
    
    /// @notice Mapping of author address to citation count
    mapping(address => uint256) public authorCitationCount;
    
    // =============================================================================
    // Constructor
    // =============================================================================
    
    constructor() {
        // Contract deployed - ready to track citations!
        totalCitations = 0;
        totalPaid = 0;
    }
    
    // =============================================================================
    // Main Functions
    // =============================================================================
    
    /**
     * @notice Pay an author for citing their knowledge
     * @dev This is the core x402 function - called by AI agents to compensate creators
     * @param _author Address of the content author to pay
     * @param _contentHash Hash/ID of the content being cited (for attribution)
     * 
     * Requirements:
     * - msg.value must be > 0 (must send CRO)
     * - _author must not be zero address
     * - _author must not be the payer (can't pay yourself)
     * 
     * Emits a {Citation} event with full attribution details
     */
    function payCitation(
        address payable _author,
        string memory _contentHash
    ) external payable {
        
        // =========================================================================
        // Input Validation
        // =========================================================================
        
        require(msg.value > 0, "CogniShare: Payment must be greater than 0");
        require(_author != address(0), "CogniShare: Author cannot be zero address");
        require(_author != msg.sender, "CogniShare: Cannot pay yourself");
        require(bytes(_contentHash).length > 0, "CogniShare: Content hash cannot be empty");
        
        // =========================================================================
        // Payment Execution
        // =========================================================================
        
        // Transfer CRO to author immediately (fail-fast pattern)
        (bool success, ) = _author.call{value: msg.value}("");
        require(success, "CogniShare: Payment transfer failed");
        
        // =========================================================================
        // State Updates (after successful payment)
        // =========================================================================
        
        // Update global stats
        totalCitations += 1;
        totalPaid += msg.value;
        
        // Update author-specific stats
        authorEarnings[_author] += msg.value;
        authorCitationCount[_author] += 1;
        
        // =========================================================================
        // Event Emission (creates on-chain record)
        // =========================================================================
        
        emit Citation(
            msg.sender,      // payer (AI agent)
            _author,         // author (content creator)
            _contentHash,    // content identifier
            msg.value,       // amount paid in Wei
            block.timestamp  // when it happened
        );
    }
    
    /**
     * @notice Batch payment for multiple citations (gas optimization)
     * @dev Pays multiple authors in a single transaction
     * @param _authors Array of author addresses
     * @param _contentHashes Array of content hashes (must match authors length)
     * @param _amounts Array of amounts to pay each author (must match authors length)
     * 
     * Requirements:
     * - All arrays must have the same length
     * - msg.value must equal sum of all _amounts
     * - All individual payment requirements apply
     */
    function batchPayCitations(
        address payable[] memory _authors,
        string[] memory _contentHashes,
        uint256[] memory _amounts
    ) external payable {
        
        // Validate array lengths
        require(
            _authors.length == _contentHashes.length && 
            _authors.length == _amounts.length,
            "CogniShare: Array length mismatch"
        );
        
        // Calculate expected total
        uint256 expectedTotal = 0;
        for (uint256 i = 0; i < _amounts.length; i++) {
            expectedTotal += _amounts[i];
        }
        
        require(msg.value == expectedTotal, "CogniShare: Incorrect total payment");
        
        // Process each citation
        for (uint256 i = 0; i < _authors.length; i++) {
            require(_authors[i] != address(0), "CogniShare: Author cannot be zero address");
            require(_amounts[i] > 0, "CogniShare: Amount must be > 0");
            
            // Transfer payment
            (bool success, ) = _authors[i].call{value: _amounts[i]}("");
            
            if (success) {
                // Update stats
                totalCitations += 1;
                totalPaid += _amounts[i];
                authorEarnings[_authors[i]] += _amounts[i];
                authorCitationCount[_authors[i]] += 1;
                
                // Emit event
                emit Citation(
                    msg.sender,
                    _authors[i],
                    _contentHashes[i],
                    _amounts[i],
                    block.timestamp
                );
            } else {
                // Payment failed - emit event but continue with others
                emit PaymentFailed(_authors[i], _amounts[i]);
            }
        }
    }
    
    // =============================================================================
    // View Functions
    // =============================================================================
    
    /**
     * @notice Get statistics for a specific author
     * @param _author Address of the author
     * @return earnings Total CRO earned (in Wei)
     * @return citations Total number of times cited
     */
    function getAuthorStats(address _author) external view returns (
        uint256 earnings,
        uint256 citations
    ) {
        return (authorEarnings[_author], authorCitationCount[_author]);
    }
    
    /**
     * @notice Get global protocol statistics
     * @return citations Total citations across all authors
     * @return paid Total CRO distributed (in Wei)
     */
    function getGlobalStats() external view returns (
        uint256 citations,
        uint256 paid
    ) {
        return (totalCitations, totalPaid);
    }
}

