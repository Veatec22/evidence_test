<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	export let data;
</script>

<EvidenceDefaultLayout {data} logo="/logo.png" title="test_title" builtWithEvidence={false} githubRepo="https://github.com/Veatec22/evidence_test" hideBreadcrumbs={true} >
	<slot slot="content" />
</EvidenceDefaultLayout>
