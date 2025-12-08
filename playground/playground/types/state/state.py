import json
from pathlib import Path
from playground.types.protocol.validators import ValidatorsData
from playground.types.state.alpha import Alpha
from playground.types.state.eta import Eta
from playground.types.state.omega import AllReadyWRs, Omega
from playground.types.state.pi import AllValidatorStats, Pi, AllServiceStats, AllCoreStats
from playground.types.state.psi import Psi, PsiB, PsiG, PsiO, PsiW
from playground.types.state.kappa import Kappa
from playground.types.state.lambda_ import Lambda_
from playground.types.state.rho import Rho, OptionalWorkReportState
from playground.types.state.tau import Tau
from playground.types.state.chi import Chi, ChiZ, ChiA
from playground.types.state.iota import Iota
from playground.types.state.theta import Theta
from playground.types.state.xi import Xi
from playground.types.state.beta import Beta, BetaHistory, BeefyBelt
from playground.types.state.phi import Phi
from playground.types.state.gamma import Gamma, GammaA, GammaP, GammaZ
from playground.types.state.delta import (
    Delta,
    AccountData,
    Timestamps,
    AccountLookup,
    AccountPreimages,
    AccountStorage,
)
from playground.types.state.sigma import Sigma
from playground.types.work import WorkDependencies
from playground.utils.constants import CORE_COUNT, EPOCH_LENGTH
from playground.types.protocol.crypto import OpaqueHash, Hash
from playground.types.protocol.core import Balance, Gas, ServiceId
from tsrkit_types.bytes import Bytes
from tsrkit_types.integers import U32
from tsrkit_types.null import Null
from playground.types.state.gamma import GammaS, GammaSFallback


class GhostState(Sigma):
    
    @staticmethod
    def detransform(state: dict) -> "GhostState":
        """Inverse of transform"""
        delta = {}
        for key, value in sorted(state.items(), key=lambda x: x[0], reverse=True):
            # Start with finding all core state components 1-15
            # if (key[0] <= 15) and bytes(key[0:32]) == 0:
            if int(key[0]) <= 15 and int(key[0]) > 0:
                if int(key[0]) == 1:
                    alpha, _ = Alpha.decode_from(bytes(value))
                elif int(key[0]) == 2:
                    phi, _ = Phi.decode_from(bytes(value))
                elif int(key[0]) == 3:
                    beta, _ = Beta.decode_from(bytes(value))
                elif int(key[0]) == 4:
                    gamma, _ = Gamma.decode_from(bytes(value))
                elif int(key[0]) == 5:
                    psi, _ = Psi.decode_from(bytes(value))
                elif int(key[0]) == 6:
                    eta, _ = Eta.decode_from(bytes(value))
                elif int(key[0]) == 7:
                    iota, _ = Iota.decode_from(bytes(value))
                elif int(key[0]) == 8:
                    kappa, _ = Kappa.decode_from(bytes(value))
                elif int(key[0]) == 9:
                    lambda_, _ = Lambda_.decode_from(bytes(value))
                elif int(key[0]) == 10:
                    rho, _ = Rho.decode_from(bytes(value))
                elif int(key[0]) == 11:
                    tau, _ = Tau.decode_from(bytes(value))
                elif int(key[0]) == 12:
                    chi, _ = Chi.decode_from(bytes(value))
                elif int(key[0]) == 13:
                    pi, _ = Pi.decode_from(bytes(value))
                elif int(key[0]) == 14:
                    omega, _ = Omega.decode_from(bytes(value))
                elif int(key[0]) == 15:
                    xi, _ = Xi.decode_from(bytes(value))
                elif int(key[0]) == 16:
                    theta, _ = Theta.decode_from(bytes(value))

            # Then find all services (first byte is 255, rest is service id)
            elif int(key[0]) == 255:
                service_id = int.from_bytes(bytes(Bytes([key[1], key[3], key[5], key[7]])))
                total_offset = 0
                ac, offset = OpaqueHash.decode_from(bytes(value), total_offset)
                total_offset += offset
                ab, offset = Balance.decode_from(bytes(value), total_offset)
                total_offset += offset
                ag, offset = Gas.decode_from(bytes(value), total_offset)
                total_offset += offset
                am, offset = Gas.decode_from(bytes(value), total_offset)
                total_offset += offset
                ao, offset = Gas.decode_from(bytes(value), total_offset)
                total_offset += offset
                ai, offset = U32.decode_from(bytes(value), total_offset)
                total_offset += offset
                delta[service_id] = AccountData(
                    storage=AccountStorage({}),
                    preimages=AccountPreimages({}),
                    lookup=AccountLookup({}),
                    code_hash=Bytes[32](ac),
                    balance=Balance(ab),
                    gas_limit=Gas(ag),
                    min_gas=Gas(am),
                )

            else:
                if Bytes(key[7:0:-2]) == Bytes(2**32 - 1):
                    # populating the storage
                    service_id = int.from_bytes(bytes(Bytes(key[0:7:2])))
                    delta[service_id].storage[
                        Bytes[32](Bytes(key[8:32] + Bytes(bytearray(8))))
                    ] = value
                elif Bytes(key[7:0:-2]) == Bytes(2**32 - 2):
                    # populating the lookup
                    service_id = int.from_bytes(bytes(Bytes(key[0:7:2])))
                    delta[service_id].lookup[Hash.blake2b(value)] = value

                else:
                    # populating the timestamps
                    service_id = int.from_bytes(bytes(Bytes(key[0:7:2])))
                    TimeStamps, _ = Timestamps.decode_from(bytes(value))
                    timestamp_key = Bytes[32](
                        Bytes(key[1:8:2]) + Bytes(key[8:32]) + Bytes(bytearray(4))
                    )
                    delta[service_id].timestamps[timestamp_key] = TimeStamps

        return GhostState(
            alpha=alpha,
            phi=phi,
            beta=beta,
            theta=theta,
            gamma=gamma,
            psi=psi,
            eta=eta,
            iota=iota,
            kappa=kappa,
            lambda_=lambda_,
            rho=rho,
            tau=tau,
            chi=chi,
            pi=pi,
            omega=omega,
            xi=xi,
            delta=delta,
        )

    @staticmethod
    def genesis(genesis_path) -> "GhostState":
        """Generate the genesis state"""
        gen = json.load(open(genesis_path))
        peers = ValidatorsData.from_json(gen["peers"])
        fallback = GhostState.arrange_fallback(Bytes[32](bytes(32)), peers)

        return GhostState(
            alpha=Alpha.from_json(gen["state"]["auth_pool"]),
            beta=Beta(h=BetaHistory([]), b=BeefyBelt([])),
            theta=Theta([]),
            gamma=Gamma(a=GammaA([]), p=GammaP(peers), s=fallback, z=GammaZ(bytes(144))),
            delta=Delta.from_json(gen["state"]["accounts"]),
            eta=Eta.from_json(gen["state"]["entropy"]),
            iota=Iota(peers),
            kappa=Kappa(peers),
            lambda_=Lambda_(peers),
            rho=Rho([OptionalWorkReportState(Null) for _ in range(CORE_COUNT)]),
            tau=Tau(0),
            phi=Phi.from_json(gen["state"]["auth_queue"]),
            chi=Chi(
                chi_m=ServiceId(0),
                chi_a=ChiA([ServiceId(0) for _ in range(CORE_COUNT)]),
                chi_v=ServiceId(0),
                chi_z=ChiZ({})
            ),
            psi=Psi(good=PsiG([]), bad=PsiB([]), wonky=PsiW([]), offenders=PsiO([])),
            pi=Pi(
                vals_current=AllValidatorStats.empty(),
                vals_last=AllValidatorStats.empty(),
                cores=AllCoreStats.empty(),
                services=AllServiceStats({}),
            ),
            omega=Omega([AllReadyWRs([]) for _ in range(EPOCH_LENGTH)]),
            xi=Xi([WorkDependencies([]) for _ in range(EPOCH_LENGTH)]),
        )
        
    @staticmethod
    def arrange_fallback(entropy: Bytes, validators: Kappa) -> GammaS:
        """
        This function is to be called in case the ticketing system fails to accumulate valid
        tickeys.
        https://graypaper.fluffylabs.dev/#/68eaa1f/0edf020edf02?v=0.6.4
        Args:
            Etn`2 - Upcoming eta2 or current eta1
            Kappa - List of current validators
        Returns:
            GammaSFallback - Set of Bandersnatch keys
        """
        # Loop through epoch size
        fallback = []
        for i in range(EPOCH_LENGTH):
            # Add entropy to encoded4(i)
            hashed = Hash.blake2b(bytes(entropy) + U32(i).encode())
            index, _ = U32.decode_from(bytes(Bytes(hashed[:4])))
            val_key = validators[int(index) % len(validators)].bandersnatch
            fallback.append(val_key)
        return GammaS(GammaSFallback(fallback))
    
    
state = GhostState.genesis(genesis_path=Path(__file__).parents[2] / "genesis.json")