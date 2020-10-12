---
layout: post
title: Most efficient probabilistic datastructure in go
tags: [golang, bloomfilter, cuckoofilter]
---

Probabilistic datastructes are a useful tool for every programmers tool belt. Imagine you have an expensive lookup operation, for example fetching a file over the network or hitting a slow, huge database. You only want to spend time and resources on this call if there's actually a result to retrieve!

This is where probabilistic filters come in handy: They are a lightweight datastructure that provide a lookup function that

1. returns `false` if and only if the key is missing
2. returns `true` if the key is available with high likelihood

After evaluating the existing implementations on Github, I created a new optimized one at [panmari/cuckoofilter](http://github.com/panmari/cuckoofilter).

## Background

We'll look at two different algorithms that are used for implementing probabilistic filters

* [Bloom filters](https://en.wikipedia.org/wiki/Bloom_filter)
* [Cuckoo filters](https://en.wikipedia.org/wiki/Cuckoo_filter)

[This page](https://bdupras.github.io/filter-tutorial/) does an awesome job explaining the theory behind, and differences between the two. Here I'm focusing on comparing implementations.

## How to evaluate implementations

As established above, these datastructures are probabilistic: When they return `true`, there's a chance that the key is still not present in the underlying set. We consider a this case a *false positive*. The rate of false positives is a function of the consumed memory for all filters.

Evaluating this trade-off is my primary goal. Secondary, I'm also interested in the benchmark timings when interacting with the filter.
Where possible, parameters were chosen to give comparable false positive rates (with a target of `0.001`).

## The evaluation

I found these popular implementations on Github and gave them all a spin

* [AndreasBriese/bbloom](http://github.com/AndreasBriese/bbloom)
* [panmari/cuckoofilter](http://github.com/panmari/cuckoofilter)
* [seiflotfy/cuckoofilter](http://github.com/seiflotfy/cuckoofilter)
* [steakknife/bloomfilter](http://github.com/steakknife/bloomfilter)
* [vedhavyas/cuckoo-filter](http://github.com/vedhavyas/cuckoo-filter)

The code used for the evaluation is [in this repo](https://github.com/panmari/compare_probabilistic_filters).

### Memory consumption

Only `vedhavyas/cuckoo-filter` sticks out here for using much more memory. Also note how `panmari/cuckoofilter` uses double the memory of `seiflotfy/cuckoofilter` (more on this later).

![Memory consumption by implementation and number of entries](/assets/img/cuckoo/Memory usage by number of entries.svg)

### False positive rate

Again some outlier with `seiflotfy/cuckoofilter` and `vedhavyas/cuckoo-filter`. They both don't offer ways to parametrize false positive rate.

![Memory consumption by implementation and number of entries](/assets/img/cuckoo/False positive rate by number of entries.svg)

Removing these two entries paints a clearer image among the other contenders.

![Memory consumption by implementation and number of entries](/assets/img/cuckoo/False positive rate by number of entries (zoomed in).svg)

### Benchmarks

Note this benchmark is single threaded. That puts some libraries at a disadvantage as they only offer thread safe methods (using an internal lock).

#### Insertion

```
InsertBloomFilter-4              165µs ± 2%
InsertBBloom-4                  30.9µs ± 0%
InsertSeiflotfyCuckoo-4         43.0µs ± 0%
InsertPanmariCuckoo-4           18.9µs ± 1%
InsertVedhavyasCuckoo-4          176µs ± 0%
```

#### Contains #1

```
ContainsTrueBloom-4              150µs ± 1%
ContainsTrueBBloom-4            29.0µs ± 1%
ContainsTrueSeiflotfyCuckoo-4   19.9µs ± 2%
ContainsTruePanmariCuckoo-4     16.7µs ± 0%
ContainsTrueVedhavyasCuckoo-4    143µs ± 3%
```

#### Contains benchmark #2

```
ContainsFalseBloom-4             152µs ± 1%
ContainsFalseBBloom-4           26.8µs ± 0%
ContainsFalseSeiflotfyCuckoo-4  21.0µs ± 0%
ContainsFalsePanmariCuckoo-4    24.7µs ± 0%
ContainsFalseVedhavyasCuckoo-4   148µs ± 2%
```

## Conclusion

In terms of false positiv rate vs memory trade-off, `steakknife/bloomfilter` and `panmari/cuckoofilter` stand out. Both give great value for the memory you invest!

When it comes to the runtime benchmarks of `Contains` calls, the cuckoo filters tend to be faster than the bloom filters. There's an good explanation for that: Cuckoo filters only need to check two positions, i.e. have at most two cache misses. Bloom filters need to access memory locations for all hash functions, i.e can have up to `k` cache misses.

Configurability is better for bloom filters: all implementations tested have construction time parameters to tweak the memory/false positive ratio trade-off. For Cuckoo filters, this is harder and backed into all implementations tested.
This is also how my own implementation at `panmari/cuckoofilter` acchieves a better false positive rate while using double the memory of `seiflotfy/cuckoofilter`: It uses a fingerprint size of `16 bit`, as opposed to `8 bit`.

The authors of ["Cuckoo Filter: Better Than Bloom"](https://www.cs.cmu.edu/~dga/papers/cuckoo-conext2014.pdf) derived the relation between fingprint size `f` and false positive rate `r`:

```
f >= log2(2 * 4/r) bits
```

With the 16 bit fingerprint, you can expect `r ~= 0.0001`. 8 bit fingerprints correspond to `r ~= 0.03`.

As most of the time in software engineering, it comes down to trade-offs.
