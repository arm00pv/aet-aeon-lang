#!/usr/bin/env python3
"""
Test All AET & AEON Improvements
Run every module to verify functionality
"""

import sys
import time
sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src')

from aet_state import AET
from aet_differentiable import AETDifferentiable, DAEModel
from aet_verification import VerificationHook
from aet_multi_strategy import MultiStrategyAET
from aet_nlp import AETNLP
from aet_benchmark import profile_aet_expression

from aeon_self_scaling import SelfScalingAEONNode
from aeon_dynamic_rag import DynamicRAGSystem
from aeon_cluster import DistributedCluster
from knowledge_graph import KnowledgeGraphAEON
from refactoring import AutonomicRefactoring

def test_all_modules():
    """Run all improvement tests"""
    
    print("=" * 80)
    print("TESTING ALL IMPROVEMENTS")
    print("=" * 80)
    
    test_results = []
    failed = []
    
    # ===================== AET MODULES =====================
    print("\n[1/5] Testing AET DAET Module...\n")
    
    try:
        daet = AETDifferentiable(dim=2048)
        model = DAEModel(dim=2048)
        result = model.optimize(target=100)
        print(f"  ✅ DAET: optimize() works, result={result}")
        test_results.append(("AET DAET", True))
    except Exception as e:
        print(f"  ❌ DAET: {e}")
        failed.append("daet")
    
    print("[2/5] Testing AET Verification Module...")
    try:
        hook = VerificationHook()
        theorem = "Sum is commutative"
        verified = hook.auto_verify("State(2048)(⊕, 1, 2)", theorem)
        print(f"  ✅ Verification: {theorem} → verified={verified}")
        test_results.append(("AET Verification", True))
    except Exception as e:
        print(f"  ❌ Verification: {e}")
        failed.append("verification")
    
    print("[3/5] Testing AET Multi-Strategy Module...")
    try:
        solver = MultiStrategyAET()
        problem = "solve_quadratic"
        variants = solver.generate_variants(problem)
        print(f"  ✅ Multi-strategy: Generated {len(variants)} variants")
        test_results.append(("AET Multi-strategy", True))
    except Exception as e:
        print(f"  ❌ Multi-strategy: {e}")
        failed.append("multi_strategy")
    
    print("[4/5] Testing AET NLP Translator...")
    try:
        translator = AETNLP()
        aet_expr = translator.translate_to_aet("sum of first n integers")
        print(f"  ✅ NLP Translator: 'sum...' → {aet_expr}")
        test_results.append(("AET NLP", True))
    except Exception as e:
        print(f"  ❌ NLP Translator: {e}")
        failed.append("nlp")
    
    print("[5/5] Testing AET Benchmark Suite...")
    try:
        profile = profile_aet_expression("State(2048)(⊕, 1, 2)")
        print(f"  ✅ Benchmark: time={profile['time_ms']*1000:.2f}ms, ops/sec={profile['throughput_ops_sec']:.0f}")
        test_results.append(("AET Benchmark", True))
    except Exception as e:
        print(f"  ❌ Benchmark: {e}")
        failed.append("benchmark")
    
    # ===================== AEON MODULES =====================
    print("\n[6/15] Testing AEON Self-Scaling Node...")
    try:
        import asyncio
        
        async def test_scaling():
            node = SelfScalingAEONNode(cluster_size=2, verbose=False)
            await node.scale_based_on_complexity(task_complexity=0.7)
            print(f"  ✅ Self-scaling: Active nodes: {len(node) if hasattr(node, '_active_nodes') else 1}")
        
        asyncio.run(test_scaling())
        test_results.append(("AEON Self-Scaling", True))
    except Exception as e:
        print(f"  ❌ Self-Scaling: {e}")
        failed.append("self_scaling")
    
    print("[7/15] Testing AEON Dynamic RAG System...")
    try:
        rag = DynamicRAGSystem(dimension=2048, chunk_size=500)
        rag.add_chunk("Test content", embedding=rag.embed("Test"))
        results = rag.query("Test query", k=1)
        print(f"  ✅ RAG: Found {results['num_results']} chunks")
        test_results.append(("AEON RAG", True))
    except Exception as e:
        print(f"  ❌ RAG: {e}")
        failed.append("rag")
    
    print("[8/15] Testing AEON Distributed Cluster...")
    try:
        cluster = DistributedCluster(num_workers=2, embedding_dim=2048)
        task = "Solve equation"
        result = cluster.add_task(task)
        print(f"  ✅ Cluster: Processed task, workers: {len(cluster._workers)}")
        test_results.append(("AEON Cluster", True))
    except Exception as e:
        print(f"  ❌ Cluster: {e}")
        failed.append("cluster")
    
    print("[9/15] Testing AEON Knowledge Graph...")
    try:
        kg = KnowledgeGraphAEON()
        kg.add_node("P1", {"label": "Person"})
        kg.add_edge("P1", "P2", {"type": "knows"})
        path = kg.find_path("P1", "P2")
        print(f"  ✅ Knowledge Graph: Path={path}")
        test_results.append(("AEON Knowledge Graph", True))
    except Exception as e:
        print(f"  ❌ Knowledge Graph: {e}")
        failed.append("knowledge_graph")
    
    print("[10/15] Testing AEON Refactoring System...")
    try:
        refactor = AutonomicRefactoring()
        report = refactor.refactor("aet_state.py", "performance")
        print(f"  ✅ Refactoring: Changes={report.changes_made}")
        test_results.append(("AEON Refactoring", True))
    except Exception as e:
        print(f"  ❌ Refactoring: {e}")
        failed.append("refactoring")
    
    # ===================== SUMMARY =====================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = [mod for mod, success in test_results if success]
    total_passed = len(passed)
    total_failed = len(failed)
    
    print(f"\n✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"\nTest results:")
    for mod, success in test_results:
        status = "[✅]" if success else "[❌]"
        print(f"  {status} {mod}")
    
    if not failed:
        print("\n🎉 ALL IMPROVEMENTS VALIDATED SUCCESSFULLY!")
    else:
        print(f"\n⚠️  {total_failed} improvements failed validation.")
    
    return test_results, failed


if __name__ == "__main__":
    test_all_modules()
