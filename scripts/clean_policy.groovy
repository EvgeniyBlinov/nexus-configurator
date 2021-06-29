import org.sonatype.nexus.cleanup.storage.CleanupPolicyStorage;
def policyStorage = container.lookup(CleanupPolicyStorage.class.getName());
def cleanupPolicy = policyStorage.newCleanupPolicy();

if (!policyStorage.get('docker_old')) {
  cleanupPolicy.setName('docker_old');
  cleanupPolicy.setNotes('Clean old docker images');
  cleanupPolicy.setMode('deletion');
  cleanupPolicy.setFormat('docker');
  cleanupPolicy.setCriteria(['lastDownloaded':'3456000']);
  policyStorage.add(cleanupPolicy);
}
