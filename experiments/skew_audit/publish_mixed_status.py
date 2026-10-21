"""Authorized dated status notice only; reuse the guarded one-edit publisher."""
import publish_rank_correction as publisher


if __name__ == '__main__':
    publisher.OUT = publisher.ROOT / 'results/mixed-biweight-status-maintenance'
    publisher.main()
