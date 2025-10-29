// Script to add "Mike Horan" name to all outgoing messages on messages.google.com
// Paste this into Chrome DevTools Console (F12)

(function() {
    'use strict';
    
    const YOUR_NAME = 'Mike Horan';
    
    // Function to add name to a single outgoing message
    function addNameToMessage(messageWrapper) {
        // Check if this is an outgoing message and doesn't already have a name
        if (!messageWrapper.classList.contains('outgoing')) {
            return;
        }
        
        const msgPartsContainer = messageWrapper.querySelector('.msg-parts-container');
        if (!msgPartsContainer) {
            return;
        }
        
        // Check if name already exists
        if (msgPartsContainer.querySelector('.participant-display-name')) {
            return;
        }
        
        // Check if this is a first message in bundle
        const msgRow = messageWrapper.querySelector('.msg-row');
        const isFirstInBundle = msgRow && msgRow.classList.contains('first-msg-in-bundle');
        
        if (!isFirstInBundle) {
            return; // Only add name to first message in bundle
        }
        
        // Create the name element matching incoming message structure
        const nameDiv = document.createElement('div');
        nameDiv.className = 'participant-display-name ng-star-inserted';
        nameDiv.setAttribute('data-color', 'blue'); // You can change the color if needed
        nameDiv.style = '';
        
        const nameTextDiv = document.createElement('div');
        nameTextDiv.className = 'participant-display-name-text';
        nameTextDiv.setAttribute('aria-label', YOUR_NAME);
        nameTextDiv.textContent = ` ${YOUR_NAME} `;
        
        nameDiv.appendChild(nameTextDiv);
        
        // Insert before the first msg-part-with-menu
        const firstMsgPart = msgPartsContainer.querySelector('.msg-part-with-menu');
        if (firstMsgPart) {
            msgPartsContainer.insertBefore(nameDiv, firstMsgPart);
            console.log('Added name to outgoing message');
        }
    }
    
    // Function to process all outgoing messages
    function processAllMessages() {
        const outgoingMessages = document.querySelectorAll('mws-message-wrapper.outgoing');
        console.log(`Found ${outgoingMessages.length} outgoing messages`);
        
        outgoingMessages.forEach(msg => {
            addNameToMessage(msg);
        });
    }
    
    // Initial processing
    console.log('Starting to add names to outgoing messages...');
    processAllMessages();
    
    // Set up MutationObserver to watch for new messages
    const observer = new MutationObserver((mutations) => {
        let shouldProcess = false;
        
        for (const mutation of mutations) {
            // Check if new nodes were added
            if (mutation.addedNodes.length > 0) {
                for (const node of mutation.addedNodes) {
                    // Check if the added node is a message wrapper or contains message wrappers
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'MWS-MESSAGE-WRAPPER' || 
                            node.querySelector('mws-message-wrapper')) {
                            shouldProcess = true;
                            break;
                        }
                    }
                }
            }
            
            if (shouldProcess) break;
        }
        
        if (shouldProcess) {
            // Use a small timeout to batch multiple mutations
            setTimeout(() => {
                processAllMessages();
            }, 100);
        }
    });
    
    // Find the messages container and observe it
    const messagesContainer = document.querySelector('mws-conversation-scroll-container') || 
                            document.querySelector('mws-messages-list') ||
                            document.body;
    
    if (messagesContainer) {
        observer.observe(messagesContainer, {
            childList: true,
            subtree: true
        });
        console.log('MutationObserver active - watching for new messages');
    } else {
        console.warn('Could not find messages container, observer not started');
    }
    
    // Store observer globally so you can disconnect it if needed
    window.nameAdderObserver = observer;
    
    console.log('Script loaded! Your outgoing messages will now show "Mike Horan"');
    console.log('To stop: window.nameAdderObserver.disconnect()');
})();
