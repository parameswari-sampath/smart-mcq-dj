// AUTO-SUBMIT LOG EXTRACTION BOOKMARKLET
// Drag this to your bookmarks bar and click to extract logs

javascript:(function(){
    // Extract auto-submit logs from localStorage
    const logs = localStorage.getItem('autoSubmitLogs');
    if (!logs) {
        alert('No auto-submit logs found in localStorage');
        return;
    }
    
    try {
        const parsedLogs = JSON.parse(logs);
        
        // Create a download link
        const dataStr = JSON.stringify(parsedLogs, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `autoSubmitLogs_${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        // Also show in console for copying
        console.log('=== AUTO-SUBMIT LOGS ===');
        console.log('Copy this JSON to a file for analysis:');
        console.log(dataStr);
        
        alert(`Downloaded ${parsedLogs.length} log entries as ${exportFileDefaultName}`);
        
    } catch (error) {
        console.error('Error extracting logs:', error);
        alert('Error extracting logs: ' + error.message);
    }
})();

// ALTERNATIVE: Console command for manual extraction
/*
To manually extract logs, paste this in browser console:

const logs = localStorage.getItem('autoSubmitLogs');
if (logs) {
    const parsedLogs = JSON.parse(logs);
    console.log('=== AUTO-SUBMIT LOGS FOR ANALYSIS ===');
    console.log(JSON.stringify(parsedLogs, null, 2));
    
    // Create downloadable file
    const dataStr = JSON.stringify(parsedLogs, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = 'autoSubmitLogs_' + new Date().toISOString().split('T')[0] + '.json';
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    console.log('Downloaded ' + parsedLogs.length + ' log entries');
} else {
    console.log('No auto-submit logs found');
}
*/